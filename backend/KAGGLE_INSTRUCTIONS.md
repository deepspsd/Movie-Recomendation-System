# 🚀 Kaggle Training Instructions

## Complete Step-by-Step Guide for Kaggle Notebooks

Since Google Colab is out of free time, use Kaggle instead! Kaggle gives you **30 hours/week** of free GPU time.

---

## 📋 What You'll Do

1. Create a Kaggle account (if you don't have one)
2. Upload the notebook to Kaggle
3. Enable Internet and GPU
4. Run all cells to train models
5. Download the trained model file
6. Place it in your backend folder

**Total Time:** 10-30 minutes (depending on sample size)

---

## 🎯 Step 1: Create Kaggle Account

1. **Go to:** https://www.kaggle.com/
2. **Click "Register"** (top right)
3. **Sign up** with Google/Email
4. **Verify your phone number** (required for GPU access)

---

## 📤 Step 2: Upload Notebook to Kaggle

### **Method 1: Direct Upload (Easiest)**

1. **Go to:** https://www.kaggle.com/code
2. **Click "New Notebook"** (blue button)
3. **Click "File"** → **"Import Notebook"**
4. **Click "Upload"** tab
5. **Select:** `COLAB_TRAINING_NOTEBOOK.ipynb` from your backend folder
6. **Click "Import"**

### **Method 2: Copy-Paste**

1. **Go to:** https://www.kaggle.com/code
2. **Click "New Notebook"**
3. Open your `COLAB_TRAINING_NOTEBOOK.ipynb` in a text editor
4. Copy all content
5. Paste into Kaggle cells

---

## ⚙️ Step 3: Configure Kaggle Settings

**IMPORTANT:** You must enable these settings:

### **Enable Internet (Required)**

1. **Click the ⚙️ Settings icon** (right sidebar)
2. **Find "Internet"**
3. **Toggle it ON** (blue)
4. This allows downloading the dataset

### **Enable GPU (Optional but Recommended)**

1. In Settings (right sidebar)
2. **Find "Accelerator"**
3. **Select "GPU"** (instead of None)
4. This makes training 2-3x faster

### **Session Options**

- **Persistence:** Turn ON to save files between sessions
- **Language:** Python
- **Environment:** Latest available

---

## 🚀 Step 4: Run the Notebook

### **Option A: Run All at Once (Recommended)**

1. **Click "Run All"** (top toolbar, or Ctrl+/)
2. **Wait for all cells to complete** (~10-30 minutes)
3. **Monitor progress** in the output
4. **Go to Step 5** when done

### **Option B: Run Cell by Cell**

Click the ▶️ play button on each cell:

1. **Cell 1:** Downloads dataset (2-3 min)
2. **Cell 2:** Installs libraries (1 min)
3. **Cell 3:** Loads model class (instant)
4. **Cell 4:** Loads data (2-3 min)
5. **Cell 5:** Formats data (1 min)
6. **Cell 6:** Trains models (5-25 min) ⏰ **Longest step**
7. **Cell 7:** Saves model (instant)
8. **Cell 8:** Prepares download (instant)

---

## 📥 Step 5: Download the Trained Model

### **Kaggle Download Process:**

1. **Click "Save Version"** (top right, blue button)
   - Or press `Ctrl + S`

2. **Select "Save & Run All"** (Quick Save option)
   - This ensures all outputs are saved

3. **Wait for notification** "Version saved successfully"
   - Check the notification bell (top right)

4. **Click "Output"** tab (right sidebar)
   - You'll see: `collaborative_filtering_trained.pkl`

5. **Click the download icon** (⬇️) next to the file
   - Or right-click → Download

6. **File downloads to your browser's download folder**

---

## 📁 Step 6: Place the Downloaded File

### **Windows:**

1. **Find the file:**
   ```
   C:\Users\YourName\Downloads\collaborative_filtering_trained.pkl
   ```

2. **Move it to:**
   ```
   d:\Movie recommendation system\backend\saved_models\collaborative_filtering_trained.pkl
   ```

3. **Verify the path:**
   ```
   backend/
   └── saved_models/
       └── collaborative_filtering_trained.pkl  ← Should be here
   ```

---

## ✅ Step 7: Verify It Works

1. **Start your backend:**
   ```bash
   cd "d:\Movie recommendation system\backend"
   python main.py
   ```

2. **Check the logs:**
   - You should see: "Model loaded successfully"

3. **Test recommendations:**
   - Go to: http://localhost:8000/docs
   - Try the `/api/recommendations/` endpoints

---

## 🎛️ Training Options (OPTIMIZED TO PREVENT CRASHES)

In **Cell 5**, you can adjust the sample size:

```python
SAMPLE_SIZE = 50000  # RECOMMENDED - prevents kernel crashes
```

### **Recommended for Kaggle (UPDATED):**

| Sample Size | Training Time | Memory Usage | Crash Risk |
|-------------|---------------|--------------|------------|
| 50,000 | 5-10 min | LOW ✅ | **SAFE** |
| 100,000 | 10-15 min | MEDIUM | Moderate |
| 200,000 | 20-30 min | HIGH | **RISKY** |
| 500,000+ | 30-60 min | VERY HIGH | **DANGEROUS** |

**⚠️ IMPORTANT:** Start with 50,000 to avoid crashes. The notebook has been optimized for memory efficiency!

---

## 💡 Kaggle Tips & Tricks

### **1. Save Your Work Often**
- Click "Save Version" every 10-15 minutes
- Kaggle sessions can timeout after 9 hours

### **2. Use GPU Acceleration**
- Always enable GPU in settings
- Makes training 2-3x faster
- Free for 30 hours/week

### **3. Monitor Resource Usage**
- Check RAM/Disk usage in bottom right
- If RAM is full, reduce SAMPLE_SIZE

### **4. Download Immediately**
- After training completes, download the model right away
- Don't close the browser until download finishes

### **5. Version Control**
- Each "Save Version" creates a snapshot
- You can go back to previous versions
- Useful if something goes wrong

---

## 🔧 Troubleshooting

### **"Internet is disabled"**
- Go to Settings (⚙️) → Turn ON Internet
- This is required for downloading the dataset

### **"Session timed out"**
- Kaggle sessions last 9 hours max
- Save your work and restart
- The model file is saved in Output

### **"Out of memory" or "Kernel Crashed"**
- **Solution 1:** Reduce SAMPLE_SIZE to 30,000 or less
- **Solution 2:** Restart the kernel: Kernel → Restart
- **Solution 3:** Disable GPU (use CPU only):
  ```python
  model = CollaborativeFilteringModel(use_gpu=False)
  ```
- **Solution 4:** Use minimal settings:
  ```python
  SAMPLE_SIZE = 20000
  model.train_svd_model(n_components=20)
  model.train_knn_model(n_neighbors=10)
  model.train_als_model(n_factors=20, n_iterations=3)
  ```

**📖 See KAGGLE_OPTIMIZATION_GUIDE.md for detailed troubleshooting**

### **"Can't find the .pkl file"**
- Make sure you clicked "Save Version"
- Check the "Output" tab (right sidebar)
- File should be listed there

### **"Download not starting"**
- Try right-click → Save As
- Or copy the file path and download manually
- Check if pop-ups are blocked

---

## 🆚 Kaggle vs Colab Comparison

| Feature | Kaggle | Google Colab |
|---------|--------|--------------|
| **Free GPU Time** | 30 hrs/week | Limited |
| **RAM** | 16-30 GB | 12 GB |
| **Disk Space** | 73 GB | 100 GB |
| **Session Length** | 9 hours | 12 hours |
| **Persistence** | Yes | No |
| **Dataset Library** | Built-in | Manual |
| **Download Method** | Output tab | files.download() |

**Kaggle is better for this project!** ✅

---

## 📊 What to Expect

### **Training Progress:**

```
🤖 TRAINING MODELS
============================================================

1️⃣ Preparing data...
✅ Data prepared: X users, Y movies

2️⃣ Computing user similarity...
✅ User similarity computed

3️⃣ Training SVD...
✅ SVD trained (50 components)

4️⃣ Training KNN...
✅ KNN trained (20 neighbors)

5️⃣ Training ALS (may take a few minutes)...
  Iteration 1/10, RMSE: 1.2345
  Iteration 3/10, RMSE: 1.1234
  Iteration 5/10, RMSE: 1.0567
  Iteration 7/10, RMSE: 1.0123
  Iteration 9/10, RMSE: 0.9876
✅ ALS trained

============================================================
✅ ALL MODELS TRAINED!
============================================================
```

### **File Size:**
- 50k ratings: ~20-50 MB
- 100k ratings: ~50-100 MB
- 500k ratings: ~200-400 MB

---

## 🎯 Quick Checklist

- ✅ Kaggle account created and phone verified
- ✅ Notebook uploaded to Kaggle
- ✅ Internet enabled in Settings
- ✅ GPU enabled in Settings (optional)
- ✅ Clicked "Run All"
- ✅ Training completed successfully
- ✅ Clicked "Save Version"
- ✅ Downloaded .pkl file from Output tab
- ✅ Placed file in `backend/saved_models/`
- ✅ Backend loads model successfully

---

## 🚀 Next Steps After Training

1. **Start your backend:**
   ```bash
   cd backend
   python main.py
   ```

2. **Test recommendations:**
   - Visit: http://localhost:8000/docs
   - Try the recommendation endpoints

3. **Integrate with frontend:**
   - Your frontend can now get ML-powered recommendations!

4. **Retrain periodically:**
   - As you collect more user ratings
   - Recommended: Every 1-2 weeks

---

## 📞 Need Help?

### **Common Issues:**

1. **"Phone verification required"**
   - Kaggle requires phone verification for GPU
   - Settings → Account → Verify Phone

2. **"Quota exceeded"**
   - You've used 30 hours this week
   - Wait for weekly reset (Monday)
   - Or use CPU instead of GPU

3. **"Kernel crashed"**
   - Reduce SAMPLE_SIZE
   - Restart kernel and try again

---

## 📝 Summary

**Kaggle is perfect for your project because:**
- ✅ More free GPU time than Colab (30 hrs/week)
- ✅ Better RAM (16-30 GB)
- ✅ Persistent storage
- ✅ Easy file download via Output tab
- ✅ Built-in dataset library

**Total time:** 15-30 minutes from upload to download!

---

**Happy Training on Kaggle! 🎉**
