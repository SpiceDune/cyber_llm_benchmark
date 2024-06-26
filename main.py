# main.py
# Import the sys library
import os
from core import CyberLLMBenchmark

if __name__ == "__main__":
    # Initialize our app with the parameters received from CLI with the sys.argv
    model_dir = "models"
    models_list = []
    for file in os.listdir(model_dir):
        if file.endswith(".py") and not file.startswith("__init__"):
            models_list.append(os.path.splitext(file)[0])
    print(models_list)
    app = CyberLLMBenchmark(models_list)

    # Run our application
    app.run()
