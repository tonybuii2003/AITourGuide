
import warnings

# Ignore the specific FastText load_model warning
warnings.filterwarnings("ignore")
import fasttext

from huggingface_hub import hf_hub_download
import pandas as pd
import os
import joblib
script_dir = os.path.dirname(os.path.abspath(__file__))
class LanguageDetector:
    """
    A language detector using Facebook's FastText language identification model.
    Returns full language names for detected languages.
    """
    def __init__(
        self,
        model_repo: str = "facebook/fasttext-language-identification",
        iso_table: str = os.path.join(script_dir,"iso-639-3.tab"),
        fallback: str = "English"
    ):
        # Download and load the fastText model
        model_path = hf_hub_download(repo_id=model_repo, filename="model.bin")
        fasttext.FastText.eprint = lambda *args, **kwargs: None
        self.model = fasttext.load_model(model_path)
        self.fallback = fallback
        df = pd.read_csv(iso_table, sep="\t", dtype=str, usecols=["Id", "Ref_Name"])
        iso_map = df.set_index("Id")["Ref_Name"].to_dict()
        raw_labels = self.model.get_labels()  
        codes = [
            lbl
            .replace("__label__", "")
            .split("_", 1)[0]      # take only the ISO code before the underscore
            for lbl in raw_labels
        ]
        self.code_to_name = {
            code: iso_map.get(code, code)  # if missing, just use 'eng' or whatever
            for code in codes
        }

    def detect(self, text: str) -> str:
        if len(text) < 2 or len(text.split()) < 1:
            return self.fallback
        # Predict top label
        labels, probs = self.model.predict(text, k=1)
        code = labels[0].replace("__label__", "").replace("_Latn", "").replace("_Cyrl", "").replace("_Arab", "")
        
        confidence = probs[0]
        if confidence < 0.80:
            return self.fallback
        # Map to human-readable name or fallback to code
        return self.code_to_name.get(code, self.fallback)
