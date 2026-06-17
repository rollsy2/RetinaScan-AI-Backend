import io
import json
import base64
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.applications.efficientnet import preprocess_input
from PIL import Image
import matplotlib.cm as cm
import os


# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
IMG_SIZE     = (224, 224)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEIGHTS_PATH = os.path.join(BASE_DIR, "model_weights.weights.h5")
CLASSES_PATH = os.path.join(BASE_DIR, "classes.json")
# ─────────────────────────────────────────────
# GLOBAL MODEL STATE
# ─────────────────────────────────────────────
MODEL_LOADED = False
class_names  = []
_conv_model  = None
_gap         = None
_dense       = None


# ─────────────────────────────────────────────
# LOAD MODEL
# ─────────────────────────────────────────────
def load_model():
    global MODEL_LOADED, class_names, _conv_model, _gap, _dense

    try:
        with open(CLASSES_PATH, "r") as f:
            class_names = json.load(f)
        num_classes = len(class_names)

        base_model = tf.keras.applications.EfficientNetB0(
            weights=None, include_top=False, input_shape=(224, 224, 3)
        )
        model = tf.keras.Sequential([
            base_model,
            tf.keras.layers.GlobalAveragePooling2D(),
            tf.keras.layers.Dense(num_classes, activation="softmax"),
        ])
        # Warm-up call to build weights
        _ = model(tf.random.normal((1, 224, 224, 3)))
        model.load_weights(WEIGHTS_PATH)

        # Grad-CAM sub-models
        _eff_base   = model.layers[0]
        _last_conv  = _eff_base.get_layer("top_conv")
        _conv_model = Model(inputs=_eff_base.input, outputs=_last_conv.output)
        _gap        = model.layers[1]
        _dense      = model.layers[2]

        MODEL_LOADED = True
        print("[INFO] Model loaded successfully")

    except Exception as e:
        MODEL_LOADED = False
        print(f"[WARN] Model not loaded: {e}")


# ─────────────────────────────────────────────
# PREPROCESSING
# ─────────────────────────────────────────────
def preprocess_image(img: Image.Image):
    img         = img.convert("RGB").resize(IMG_SIZE)
    raw         = np.array(img)
    model_input = preprocess_input(raw.astype("float32"))
    model_input = np.expand_dims(model_input, 0)
    return model_input, raw


# ─────────────────────────────────────────────
# GRAD-CAM
# ─────────────────────────────────────────────
def make_gradcam_heatmap(img_array):
    img_tensor = tf.cast(img_array, tf.float32)
    with tf.GradientTape() as tape:
        conv_out = _conv_model(img_tensor)
        tape.watch(conv_out)
        pooled   = _gap(conv_out)
        preds    = _dense(pooled)
        pred_idx = tf.argmax(preds[0])
        class_ch = preds[0, pred_idx]

    grads        = tape.gradient(class_ch, conv_out)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
    heatmap      = conv_out[0] @ pooled_grads[..., tf.newaxis]
    heatmap      = tf.squeeze(heatmap)
    heatmap      = tf.maximum(heatmap, 0)
    heatmap     /= tf.math.reduce_max(heatmap) + 1e-8
    return heatmap.numpy(), preds.numpy()


def overlay_heatmap(raw_img: np.ndarray, heatmap: np.ndarray) -> str:
    h, w = raw_img.shape[:2]
    heatmap_resized = np.array(
        Image.fromarray(np.uint8(255 * heatmap)).resize((w, h), Image.LANCZOS)
    ) / 255.0
    colored = cm.jet(heatmap_resized)[:, :, :3]
    overlay = np.uint8(colored * 0.4 * 255 + raw_img * 0.6)
    buf = io.BytesIO()
    Image.fromarray(overlay).save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


# ─────────────────────────────────────────────
# FULL ANALYSIS (called from main.py)
# ─────────────────────────────────────────────
def run_analysis(img: Image.Image, filename: str) -> dict:
    if not MODEL_LOADED:
        raise RuntimeError("Model is not loaded. Check weights and classes files.")

    model_input, raw_img = preprocess_image(img)
    heatmap, preds       = make_gradcam_heatmap(model_input)
    pred_idx             = int(np.argmax(preds[0]))

    all_classes = {
        class_names[i]: round(float(preds[0][i]) * 100, 2)
        for i in range(len(class_names))
    }

    return {
        "filename":       filename,
        "prediction":     class_names[pred_idx],
        "confidence":     round(float(preds[0][pred_idx]) * 100, 2),
        "model_used":     "EfficientNetB0",
        "all_classes":    all_classes,
        "gradcam_base64": overlay_heatmap(raw_img, heatmap),
    }