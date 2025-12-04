# ⚠️ **Important Notice Before Opening the Live App**

> ### 🚨 The chat assistant **will NOT work** unless you first run the required `Inference.ipynb` notebook with **GPU enabled** *and* configure the environment variables.  
> The live webpage is only a frontend — without initializing the backend model, **nothing will respond**.

---

## 🔧 **Required Setup Before Using the Live Web App**

### **1️⃣ Open the Notebook**
Run the `Inference.ipynb` file in **Google Colab** or **Kaggle Notebook**.  
This notebook sets up the backend server required by the chat assistant.

---

## **2️⃣ Set Up Required Environment Variables**

Inside your Colab/Kaggle runtime, create an `.env` file  
(or alternatively use `%env` commands) with the following values:


INFERENCE_API_KEY=1621cb402e199697ad77c98e6fe24d8f98c4cbbcd05add9935b41a4a52cfbe10<br>
HF_TOKEN=<YOUR_HF_TOKEN><br>
MODEL_PATH=ibm-granite/granite-4.0-micro

These environment variables are essential for:

- Authenticating the inference API  
- Accessing Hugging Face model resources  
- Loading the `ibm-granite/granite-4.0-micro` model backend  

## In Order To This To Make The Chat Assistant TO Work, You Need To Follow The Above Steps & Ensure The INFERENCE_KEY Remains The Same as Given.
