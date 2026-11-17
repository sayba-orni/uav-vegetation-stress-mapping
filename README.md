# UAV vegetation mapping and tea-leaf disease segmentation

EEE 404 Robotics and Automation Laboratory group project, BUET.

This repository contains two **separate analysis pipelines** developed as part of the broader UAV-based tea-garden monitoring project:

1. **RGB vegetation mapping** — frame/image processing, Excess Green (ExG), Visible Atmospherically Resistant Index (VARI), low-index region visualization, and illustrative area-level mapping.
2. **Tea-leaf disease segmentation** — a SegFormer-based four-class semantic segmentation experiment (background, algal leaf spot, brown blight, grey blight).

These pipelines are presented separately. The available code does **not** demonstrate a single integrated, real-time UAV-to-SegFormer deployment.

## Repository layout

```text
notebooks/
  vegetation_mapping.ipynb             # Clean RGB vegetation-index demonstration
  segformer_tea_leaf_segmentation.ipynb # Organized training/evaluation notebook
scripts/
  vegetation_mapping.py                # Reusable RGB processing script
archive/
  original_mapping_colab.ipynb         # Original experiment, preserved as reference
  original_heatmap_experiments.ipynb    # Original experiments, preserved as reference
  original_segformer_colab.ipynb       # Original one-cell SegFormer Colab notebook
images/                                 # Authentic project images and SegFormer examples
videos/                                 # UAV flight recording
data/                                  # Local datasets (ignored by Git)
```

## SegFormer experiment

The original code uses `SegformerForSemanticSegmentation` and `SegformerImageProcessor` from Hugging Face Transformers. The configuration is **512 × 512 input**, **batch size 4**, **25 epochs**, **learning rate 2e-5**, and **four output classes**. The code includes training, validation, best-checkpoint selection, per-image test evaluation, and predicted-mask export.

To run the organized notebook, install dependencies from `requirements.txt` and point `ROOT` to the leaf segmentation dataset. Expected split folders are `train/`, `valid/`, and `test/`; each image is paired with a `<stem>_mask.png` mask. Inspect the notebook's class-index conventions before substituting a different dataset.

## RGB vegetation mapping

The RGB pipeline calculates ExG = 2G − R − B and VARI = (G − R)/(G + R − B), then displays low-index regions. **Low-index regions are not confirmed disease or stress labels.** The original mapping notebook also synthesizes a serpentine flight path and pseudo-GPS metadata; therefore its area maps and tile mosaics are **illustrative, not validated georeferenced orthomosaics**.

The cleaned vegetation notebook and script are simplified examples; the original exploratory processing is retained in `archive/` for transparency.

## Project photographs and results

**Drone hardware** — photograph of the group-built quadcopter and its flight-control electronics.

![Drone hardware](images/drone-hardware.png)

**ExG and VARI comparisons** — RGB image alongside vegetation-index visualizations. Low index values indicate relatively low greenness, **not independently verified disease**.

![ExG and VARI comparison](images/exg-vari-comparison.png)

**Frame extraction** — sample frames from the video-processing workflow (the displayed run reports 86 extracted frames).

![Extracted frames](images/extracted-frames.png)

**3D mapping visualization** — an illustrative spatial surface visualization, not a measured terrain or GPS-validated reconstruction.

![3D mapping visualization](images/3d-mapping.png)

**SegFormer qualitative examples** — prediction examples reproduced from the team's EEE 404 presentation (slide 25). These are separate from the UAV vegetation-index pipeline.

![SegFormer prediction examples](images/segformer-prediction-examples.png)

**Flight video:** [View drone flight recording](videos/drone-flight.mp4) (MP4; downloadable from GitHub).

## Reproducibility and limitations

- The UAV flight video and selected project figures are included. Original training datasets and model checkpoints are **not included**.
- The organized SegFormer notebook was **syntax checked**, but was not retrained or evaluated here. Metrics reported in the team presentation are not reproduced by this package.
- The vegetation pipeline and SegFormer experiment are independent pieces of the group project. The code alone does not establish individual contributions to all hardware or software components.
- The `archive/` notebooks preserve the experiments as received; use the cleaned notebooks as the starting point for new runs.

## Running

```bash
pip install -r requirements.txt
python scripts/vegetation_mapping.py --help
```

For SegFormer, open `notebooks/segformer_tea_leaf_segmentation.ipynb` and update its `ROOT` path before running cells in order. Depending on your installed Transformers version, API adjustments may be required.
