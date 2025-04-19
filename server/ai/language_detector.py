
import warnings

# Ignore the specific FastText load_model warning
warnings.filterwarnings("ignore")
import fasttext
fasttext.FastText.eprint = lambda *args, **kwargs: None
from huggingface_hub import hf_hub_download

class LanguageDetector:
    """
    A language detector using Facebook's FastText language identification model.
    Returns full language names for detected languages.
    """
    def __init__(self, model_repo="facebook/fasttext-language-identification", fallback="English"):
        # Download and load the fastText model
        model_path = hf_hub_download(repo_id=model_repo, filename="model.bin")
        self.model = fasttext.load_model(model_path)
        self.fallback = fallback
        # Mapping ISO codes to human-readable names
        self.code_to_name = {
            "af": "Afrikaans", "ar": "Arabic", "bg": "Bulgarian", "bn": "Bengali",
            "ca": "Catalan", "cs": "Czech", "cy": "Welsh", "da": "Danish",
            "de": "German", "el": "Greek", "en": "English", "es": "Spanish",
            "et": "Estonian", "fa": "Persian", "fi": "Finnish", "fr": "French",
            "gu": "Gujarati", "he": "Hebrew", "hi": "Hindi", "hr": "Croatian",
            "hu": "Hungarian", "id": "Indonesian", "it": "Italian", "ja": "Japanese",
            "kn": "Kannada", "ko": "Korean", "lt": "Lithuanian", "lv": "Latvian",
            "mk": "Macedonian", "ml": "Malayalam", "mr": "Marathi", "ne": "Nepali",
            "nl": "Dutch", "no": "Norwegian", "pa": "Punjabi", "pl": "Polish",
            "pt": "Portuguese", "ro": "Romanian", "ru": "Russian", "sk": "Slovak",
            "sl": "Slovenian", "so": "Somali", "sq": "Albanian", "sv": "Swedish",
            "sw": "Swahili", "ta": "Tamil", "te": "Telugu", "th": "Thai", "tl": "Tagalog",
            "tr": "Turkish", "uk": "Ukrainian", "ur": "Urdu", "vi": "Vietnamese",
            "zh-cn": "Chinese (Simplified)", "zh-tw": "Chinese (Traditional)"
        }

    def detect(self, text: str) -> str:
        if len(text) < 3 or len(text.split()) < 1:
            return self.fallback
        # Predict top label
        labels, probs = self.model.predict(text, k=1)
        code = labels[0].replace("__label__", "")
        confidence = probs[0]
        if confidence < 0.80:
            return self.fallback
        # Map to human-readable name or fallback to code
        return self.code_to_name.get(code, self.fallback)
