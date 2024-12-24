# Standard imports
import os

# twinLab
import twinlab as tl

# Campaign
CAMPAIGN_ID = "cosmology"
DATASET_ID = "cosmology"
PROJECT_ID = "cosmology"

# Data options
POWER_RATIO = False  # We are going to learn the ratio of the non-linear to linear spectrum
# We are going to learn the log of the (ratio of the) power spectrum
POWER_LOG = True
# We are taking data where the training points are Latin hypercube sampled
POWER_LATIN = True
TRAINING_RATIO = 1.  # Use all training data
# Retain 99.99% of the variance in the SVD/PCA decomposition of the data
SVD_VARIANCE = 0.99

# Data files
TRAINING_FILEBASE = "cosmo"
EVALUATION_FILEBASE = "eval"
GRID_DATA = "grid.csv"
NK = 100  # Number of wave-number values (pre-determined by the data file)

# Directories
DATASETS_DIR = os.path.join("data")

# Suffixes for data files
latin_thing = '_latin' if POWER_LATIN else ''
ratio_thing = '_ratio' if POWER_RATIO else ''
log_thing = '_log' if POWER_LOG else ''

# Construct training and evaluation data file names
TRAINING_DATA = TRAINING_FILEBASE+latin_thing+ratio_thing+log_thing+".csv"
EVALUATION_DATA = EVALUATION_FILEBASE+ratio_thing+log_thing+".csv"

# File paths
DATASET_PATH = os.path.join(DATASETS_DIR, TRAINING_DATA)

# Write to screen
print(f"Dataset..... {DATASET_PATH}")

dataset = tl.Dataset(DATASET_ID, PROJECT_ID)
try:
    dataset.delete()
except:
    pass
df = tl.load_dataset(DATASET_PATH)
dataset.upload(df, verbose=True)

# We will take these cosmological parameters as input
cosmological_parameters = ["Omega_c", "Omega_b", "h", "ns", "w0"]
# We will try to learn P(k) at these wavenumbers
wavenumber_columns = [f"k{i}" for i in range(NK)]
params = tl.TrainParams(
    output_explained_variance=SVD_VARIANCE, train_test_ratio=TRAINING_RATIO)

emulator = tl.Emulator(CAMPAIGN_ID, PROJECT_ID)
try:
    emulator.delete()
except:
    pass
emulator.train(dataset, cosmological_parameters,
               wavenumber_columns, params, verbose=True)
