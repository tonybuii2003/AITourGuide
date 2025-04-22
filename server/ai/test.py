import fasttext
from huggingface_hub import hf_hub_download

# Suppress FT warning
fasttext.FastText.eprint = lambda *args, **kwargs: None

# Download & load the LID model
model_path = hf_hub_download(
    repo_id="facebook/fasttext-language-identification",
    filename="model.bin"
)
model = fasttext.load_model(model_path)

# 1. Get all labels (e.g. ["__label__en", "__label__fr", ...])
labels = model.get_labels()

# 2. Strip the prefix to get just ISO codes
codes = [lbl.replace("__label__", "") for lbl in labels]

# 3. Print them all
for code in codes:
    print(code)
