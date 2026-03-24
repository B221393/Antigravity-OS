import torch
from PIL import Image
from transformers import AutoModelForCausalLM, AutoProcessor
import os

# Model ID identified from research
MODEL_ID = "zai-org/GLM-OCR"

class VisualCortex:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VisualCortex, cls).__new__(cls)
            cls._instance.model = None
            cls._instance.processor = None
            cls._instance.device = "cuda" if torch.cuda.is_available() else "cpu"
        return cls._instance

    def load_model(self):
        """Lazy loader for the massive model"""
        if self.model is not None:
            return

        print(f"Visual Cortex: Loading {MODEL_ID} on {self.device}...")
        try:
            # Using trust_remote_code=True as this is likely a custom architecture
            self.processor = AutoProcessor.from_pretrained(MODEL_ID, trust_remote_code=True)
            self.model = AutoModelForCausalLM.from_pretrained(
                MODEL_ID,
                trust_remote_code=True,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None
            )
            print("Visual Cortex: Online.")
        except Exception as e:
            print(f"Visual Cortex Initialization Failed: {e}")
            raise

    def image_to_markdown(self, image_path):
        """
        Converts an image file to Markdown text using GLM-OCR.
        """
        if not self.model:
            self.load_model()

        try:
            image = Image.open(image_path).convert('RGB')
            
            # Standard GLM-4V / VLM input format
            inputs = self.processor(images=image, text="Describe this image in detail and transcribe any text as Markdown.", return_tensors="pt")
            inputs = inputs.to(self.model.device)

            with torch.no_grad():
                outputs = self.model.generate(**inputs, max_new_tokens=1024)
                generated_text = self.processor.batch_decode(outputs, skip_special_tokens=True)[0]
            
            return generated_text
        except Exception as e:
            return f"Error analyzing image: {e}"

# Singleton exposure
_cortex = VisualCortex()

def image_to_markdown(image_path):
    return _cortex.image_to_markdown(image_path)

if __name__ == "__main__":
    # Test block
    print("Testing Visual Cortex...")
    # placeholder for test
