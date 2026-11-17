# Technical report — source text (selected sections)

> Extracted from the team EEE 404 final report. This is a **historical source transcript**, not a corrected specification. The report contains inconsistencies in SegFormer configuration and classification/segmentation attribution; the repository README and `docs/deep-learning.md` explain the verified implementations. Student-ID/individual contribution pages have been omitted.

## Original report — page 4

1  Abstract


This project presents a UAV-based autonomous system for vegetation stress mapping and early-
stage disease detection in tea gardens. A custom-built quadcopter equipped with an RGB camera
and Raspberry Pi 4 companion computer performs scheduled survey flights over large plantation
areas. Extracted video frames are geo-tagged using synthetic GPS metadata and processed through
two complementary vegetation indices — the Excess Green Index (ExG) and the Visible
Atmospherically Resistant Index (VARI) — to produce interpolated area-level stress heatmaps.

Anomalous (low-vegetation) regions flagged by the heatmap trigger a secondary close-up flight to
the suspect GPS coordinate. Acquired close-up imagery is then classified by a pre-trained SegFormer
transformer model fine-tuned on a 1,158-image tea leaf disease dataset, achieving pixel accuracy
0.977 and weighted F1-score 0.931 across seven disease classes. The end-to-end prototype was
validated at BUET campus and a Sylhet tea plantation, with a total hardware cost of approximately
BDT 50,000.





                          UAV-Based Vegetation Stress Mapping for Tea Garden  · Group 2  · Page 4

## Original report — page 5

2  Introduction

Tea cultivation is one of the most economically significant agricultural activities in Bangladesh and across
South Asia. Major tea-growing regions such as Sylhet and Chittagong Hill Tracts host estates spanning
several hundred hectares each. Early and accurate identification of foliar disease is critical to maintaining
crop yield and quality, yet current practice relies almost entirely on manual scouting by human workers — a
process that is both slow and inherently inconsistent at scale.

Unmanned Aerial Vehicles (UAVs) equipped with consumer-grade RGB cameras offer a compelling low-cost
alternative to traditional field inspection and to expensive multispectral or hyperspectral drone solutions.
By computing vegetation indices directly from the red, green, and blue channels of aerial imagery, it is
possible to produce detailed spatial maps of plant stress at centimetre-level ground resolution. When
coupled with modern deep learning architectures for semantic segmentation, the resulting pipeline can
autonomously identify, localise, and diagnose specific foliar diseases with clinically meaningful accuracy.

This report describes the design, implementation, and evaluation of such a system, comprising: (i) a custom
quadcopter  with  autonomous  mission-planning  capability;   (ii)  a  Python-based  vegetation  index
computation and heatmap generation pipeline; and  (iii) a SegFormer-based disease segmentation and
classification module. The project addresses a Complex Engineering Problem requiring multi-disciplinary
expertise spanning embedded systems, autonomous UAV navigation, computer vision, and machine
learning.


Key Contributions
• End-to-end autonomous two-stage UAV survey pipeline for tea garden disease detection.
• Dual-index vegetation analysis (ExG + VARI) for robust, illumination-resistant stress mapping.
• SegFormer fine-tuning on tea leaf disease dataset achieving 97.7% pixel accuracy.
• Low-cost prototype (BDT 50,000) demonstrating feasibility for smallholder farmers.





                          UAV-Based Vegetation Stress Mapping for Tea Garden  · Group 2  · Page 5

## Original report — page 6

3 Design

3.1 Problem Formulation (PO-b)

3.1.1  Identification of Scope
The project scope encompasses the full pipeline from UAV hardware assembly and autonomous flight,
through image acquisition, vegetation index mapping, anomaly detection, targeted re-flight, and deep-
learning disease classification. The system was validated over two distinct environments: the BUET campus
lawn (controlled) and a Sylhet tea garden (field). Autonomous pesticide spraying and real-time cloud
synchronisation are outside the current scope.

3.1.2  Literature Review
Precision agriculture using UAVs has been studied extensively over the past decade. Vegetation indices
derived from RGB imagery are widely used as proxies for plant health. The Excess Green Index (ExG = 2G −R
−B) was originally proposed by Woebbecke et al. (1995) to separate green vegetation from soil background.
The Visible Atmospherically Resistant Index (VARI = (G −R)/(G + R −B)), introduced by Gitelson et al. (2002),
provides improved robustness to lighting variation without requiring atmospheric correction.
For disease classification, convolutional neural networks (CNNs) such as ResNet and EfficientNet have
achieved strong results on leaf disease datasets. More recently, transformer-based architectures — notably
SegFormer (Xie et al., 2021) — have outperformed CNNs on semantic segmentation benchmarks while
remaining  computationally  efficient.  SegFormer's  hierarchical Mix Transformer  (MiT) encoder and
lightweight MLP decoder make it well-suited to fine-grained agricultural image segmentation.
To our knowledge, no published work integrates dual-index RGB vegetation mapping with SegFormer-based
disease segmentation in a fully autonomous closed-loop UAV pipeline for tea garden monitoring.

3.1.3 Problem Formulation
The core engineering problem is stated as follows:

Problem Statement
"How can a low-cost, autonomous UAV system detect, geo-localise, and classify vegetation stress
and foliar disease in a large tea garden using only an onboard RGB camera and edge-computing
module, with minimal human intervention?"


This constitutes a Complex Engineering Problem (CEP) because it: (i) requires integration of knowledge
from multiple engineering domains; (ii) involves competing design constraints (cost vs. accuracy, real-time
vs. batch processing); and (iii) must operate reliably in unstructured outdoor environments.





                          UAV-Based Vegetation Stress Mapping for Tea Garden  · Group 2  · Page 6

## Original report — page 7

3.1.4  Analysis of Alternative Solutions
       Approach                          Pros                              Cons

Multispectral UAV (NDVI)       Highly accurate vegetation indices          Very high cost (>USD 5,000)

Satellite remote sensing            Wide area coverage             Low resolution, high latency

Manual scouting                  Ground truth accuracy             Slow, labour-intensive, error-prone

Fixed RGB camera array              No flight risk                       Limited area coverage

Proposed: RGB UAV + DL       Low cost, automated, accurate           Requires flight planning effort
                            Table 1: Comparison of alternative disease detection approaches


3.2 Design Method (PO-a)
The system architecture follows a two-stage, closed-loop design. Stage 1 (Regular Condition) operates on a
scheduled basis; Stage 2 (Anomaly Condition) is triggered reactively when Stage 1 identifies a stressed
region. The complete flow is illustrated in Figure 1.





                        Figure: Full System Pipeline — Regular Condition and Anomaly Condition Flows



                          UAV-Based Vegetation Stress Mapping for Tea Garden  · Group 2  · Page 7

## Original report — page 8

Key design decisions:
   •  RGB-only sensing: eliminates the need for expensive multispectral sensors while still enabling two
       complementary vegetation indices.
   •   Synthetic GPS tagging: allows vegetation maps to be generated from standard video footage
       without GPS-tagged still images, reducing hardware complexity.
   •   Dual-index confirmation: requiring both ExG and VARI to flag a region reduces false positives from
         lighting variation.
   •  SegFormer over CNN: transformer architecture provides better spatial context for small irregular
        lesion shapes.


3.3 Hardware Design
The drone platform is a custom-built quadcopter based on an F450 frame with ArduPilot flight controller. A
Raspberry Pi 4 (2 GB) serves as the onboard companion computer, communicating with the flight controller
via MAVLink over serial. The RGB camera is mounted on a fixed nadir-pointing bracket for consistent
downward-facing imagery.


    Component                      Specification                               Role

Frame                      F450 450mm quadcopter                      Structural platform

Motors                   A2212 1000KV brushless ×4                    Thrust generation

ESCs                          30A SimonK ×4                     Motor speed control

Flight Controller                 Pixhawk (ArduPilot)                 Autonomous navigation

Companion Computer            Raspberry Pi 4 (2 GB)                Image capture & processing

Camera                      Samsung S860 (RGB)                           Aerial imagery

Battery                        3S 5200 mAh LiPo ×2                     Power supply

GPS Module                           u-blox M8N                            Position estimation

Propellers                         10×4.5 ×4 pairs                          Thrust & stability

                                 Table 2: Hardware bill of materials and specifications





                          UAV-Based Vegetation Stress Mapping for Tea Garden  · Group 2  · Page 8

## Original report — page 9

Figure: Drone During Normal Condition Test Flight at BUET Campus

A total of 84 flight attempts were made across bench and field settings. Bench trials (61 attempts) were
used to calibrate the flight controller PID parameters, verify motor/ESC response, and test emergency stop
behaviour. Outdoor flights (23 attempts) achieved 14 successful missions and 9 crashes (primarily due to
GPS lock loss and wind disturbance in early trials).


           Trial Category                Attempts               Successes                 Failures

Bench calibration trials                   61           —           —

Outdoor flights (BUET)                    14                    8                    6

Outdoor flights (Sylhet field)                9                    6                    3

Total                                  84               14 successful            9 crashes
                                            Table 3: Flight trial statistics




                          UAV-Based Vegetation Stress Mapping for Tea Garden  · Group 2  · Page 9

## Original report — page 10

3.4  Flight Mission Planning
Mission planning was performed using ArduPilot Mission Planner software. Two mission types were defined:

3.4.1 Normal Condition — Lawnmower Survey Mission
A  boustrophedon  (back-and-forth)  survey  pattern was programmed  over  the  target  area  with
DO_SET_CAM_TRIGG_DIST commands to trigger camera capture at fixed distance intervals (every 3.4 m ).
Key parameters for the mission:

              Parameter                                          Value

Survey area                                                         7,352 m²

Flight altitude                                                 10 m AGL

Camera angle                                                97° (forward-tilted nadir)

Flying speed                                                             0.8 m/s

Number of strips                                                 22

Footprint per image                                                    9.1 × 6.8 m

Ground resolution                                                  0.28 cm/pixel

Estimated pictures                                               591

Total distance                                           403.57 km flight plan equivalent

                                      Table 4: Sylhet survey mission parameters





                          UAV-Based Vegetation Stress Mapping for Tea Garden  · Group 2  · Page 10

## Original report — page 11

Figure: ArduPilot Mission Planner — Lawnmower Survey Mission over Sylhet Tea Garden





      Figure: Elevation Profile for Sylhet Survey Mission (Google Earth terrain data)


         UAV-Based Vegetation Stress Mapping for Tea Garden  · Group 2  · Page 11

## Original report — page 12

3.4.2 Anomaly Condition — Targeted Waypoint Mission
When the vegetation mapping pipeline identifies a suspicious GPS coordinate, Mission Planner auto-
generates a single-waypoint mission: TAKEOFF →WAYPOINT (target GPS) →DELAY (loiter for image
capture) →RETURN_TO_LAUNCH. This ensures the drone acquires a close-up image of the flagged region
without requiring manual re-piloting.





             Figure: ArduPilot Mission Planner — Anomaly Condition Targeted Flight to Flagged Disease Location

3.5 Software — Vegetation Mapping Pipeline
The mapping component  of  this  project  focuses on  transforming raw  aerial video footage  into
geographically accurate 3D surface models. This serves as the structural foundation upon which the
vegetation indices and heatmaps are subsequently projected.


3.5.1 Coordinate Transformation and Local-Planar Mapping
To process the frame-wise pseudo-GPS logs into a format suitable for 3D rendering, the raw geographic
coordinates (Latitude, Longitude, Altitude) are converted into a local Cartesian (x,y,z) system. This local-
planar transform minimizes computational overhead by using the survey's starting boundary as the origin.
This allows the system to treat the survey area as a flat grid where z represents the vertical displacement,
essential for generating topographies of the tea gardens or campus grounds




                          UAV-Based Vegetation Stress Mapping for Tea Garden  · Group 2  · Page 12

## Original report — page 13

3.5.2 3D Surface Reconstruction via Barycentric Interpolation
Because the drone extracts frames at discrete intervals, the resulting spatial data consists of "point clouds"
rather than a continuous surface. To visualize the terrain as a solid 3D map, the system employs Barycentric
Interpolation.


Triangulation: The local coordinates are used to define a triangular mesh across the flight area. Each set of
three adjacent GPS points forms a sub-plane.





                                        Figure: Geo-tagged Image to 3D visualization



Weight Calculation: For any arbitrary coordinate (x,y) within a triangle defined by vertices P1,P2,P3, the
weights w1,w2,w3 are calculated.



Surface Elevation: The interpolated height z at that specific point is then determined .
This mathematical approach ensures a smooth transition between frames, allowing for the generation of a
continuous 3D surface map.





                          UAV-Based Vegetation Stress Mapping for Tea Garden  · Group 2  · Page 13

## Original report — page 14

3.5.3 Map Rendering and Visualization Tools
The visualization suite relies on two primary open-source libraries to interpret the interpolated data:


Folium: Utilized for generating 2D interactive maps. It handles the GPS heatmap overlays on real-world
satellite tiles (such as the BUET Campus), providing a macro view of the flight trajectory and data density.


Plotly: Used to render the 3D surface maps. By applying the results of the Barycentric interpolation, Plotly
generates interactive 3D heatmaps that allow users to rotate and analyze the terrain's elevation and spatial
characteristics in real-time.

3.5.4 3D Map and Histogram generation
Frames are extracted from the flight video at a fixed interval using OpenCV. Each frame is assigned a
pseudo-GPS coordinate based on the assumed serpentine flight path, with added positional drift, path
wobble, and Gaussian noise to replicate realistic GPS jitter. Altitude, heading, and speed are also varied
over time. The result is a frame-wise pseudo-GPS log.

3.5.1 Frame Extraction and GPS Tagging
Frames are extracted from the flight video at a fixed interval using OpenCV. Each frame is assigned a
pseudo-GPS coordinate based on the assumed serpentine flight path, with added positional drift, path
wobble, and Gaussian noise to replicate realistic GPS jitter. Altitude, heading, and speed are also varied
over time. The result is a frame-wise pseudo-GPS log.





                         Figure: Synthetic Drone Flight Path — Pseudo-Georeferenced Trajectory Plot




                          UAV-Based Vegetation Stress Mapping for Tea Garden  · Group 2  · Page 14

## Original report — page 15

3.5.2 Vegetation Index Computation
For each extracted frame, two vegetation indices are computed per-pixel from the RGB channels
(normalised to [0, 1]):

                           ExG = 2G−R−B

                       VARI = (G−R)/(G+R−B+ε)
where ε is a small constant to prevent division by zero. ExG provides strong discrimination between
vegetation and bare soil under controlled illumination; VARI is preferred for varying lighting conditions as it
is atmospherically resistant. Pixels that appear dark (low-valued) in both maps simultaneously are flagged
as potentially stressed or diseased.





                        Figure: ExG and VARI Maps for Sylhet Tea Garden Frames (two sample frames)

3.5.3 Mosaic Generation and Heatmap Interpolation
All geo-referenced ExG and VARI frame thumbnails are plotted at their pseudo-GPS coordinates to form a
pseudo-georeferenced  mosaic.  An  interpolated  area-level  VARI  heatmap   is  produced  using
scipy.interpolate.griddata with cubic interpolation, providing a smooth spatial map of vegetation health
across the entire survey area. A binary "suspicious area" mask is generated by thresholding VARI below a
calibrated value.





                          UAV-Based Vegetation Stress Mapping for Tea Garden  · Group 2  · Page 15

## Original report — page 16

Figure: VARI Mosaic and ExG Mosaic of last flight image





           Figure: VARI Mosaic and ExG Mosaic mapping





UAV-Based Vegetation Stress Mapping for Tea Garden  · Group 2  · Page 16

## Original report — page 17

Figure: Interpolated Area-Level VARI Heatmap and Suspicious Area Probability Mosaic

3.6 Deep Learning — Disease Segmentation and Classification (SegFormer)

3.6.1 Dataset
The disease detection model was trained on a Tea Leaf Segmentation Dataset comprising 1,158 annotated
images. Each image is accompanied by a grayscale segmentation mask where pixel values encode disease
class. The dataset was split 80/10/10 for training, validation, and testing. Image augmentation techniques
— random horizontal/vertical flip, colour jitter, and random rotation ±15° — were applied during training
to improve generalisation.

    Pixel Value        Mask Colour (RGB visualisation)                     Disease Class

0                                     Black                            Background / Healthy

1                               Red                                      Algal Leaf Spot

2                               Green                            Brown Blight

3                                   Blue                                 Grey Blight
                                 Table 5: Pixel encoding for segmentation mask classes





                          UAV-Based Vegetation Stress Mapping for Tea Garden  · Group 2  · Page 17

## Original report — page 18

3.6.2 Model Architecture
SegFormer (Xie et al., NeurIPS 2021) is a hierarchical transformer architecture for semantic segmentation.
Its encoder  is a Mix Transformer (MiT) that generates multi-scale feature representations without
positional encoding; its decoder is a lightweight all-MLP module that aggregates features from all encoder
stages. The B2 variant was selected as a balance between model capacity and inference speed. Pre-trained
weights on ImageNet-1K were used as initialisation before fine-tuning.





                       Figure: SegFormer Architecture Diagram (MiT Encoder + MLP Decoder Pipeline)





            Figure: Deep Learning Model Pipeline: Preprocessing →SegFormer →Pixel Mapping →Classification





                          UAV-Based Vegetation Stress Mapping for Tea Garden  · Group 2  · Page 18

## Original report — page 19

3.6.3  Training Details
           Hyperparameter                                        Value

Base model                                          SegFormer-B2 (ImageNet pretrained)

Input resolution                                              512 × 512 px

Batch size                                                       8

Optimiser                                         AdamW

Learning rate                                                  6 × 10⁻⁵

LR scheduler                                                    Polynomial decay

Training epochs                                                  100

Loss function                                                 Cross-entropy (weighted)

Hardware                                                 Google Colab A100 GPU

                                    Table 6: SegFormer training hyperparameters





                          UAV-Based Vegetation Stress Mapping for Tea Garden  · Group 2  · Page 19

## Original report — page 20

4 Implementation

4.1 Hardware Assembly and Bench Testing
The quadcopter was assembled in phases. Motor and ESC wiring was completed first, followed by flight
controller mounting and calibration via Mission Planner (compass, accelerometer, radio calibration). The
Raspberry Pi was installed in a custom 3D-printed mount above the top plate and connected to the flight
controller via UART at 57,600 baud using the MAVLink2 protocol. DroneKit-Python was used on the
Raspberry Pi to send commands and read telemetry.
Bench testing involved spinning motors with propellers removed to verify PWM response and verifying
MAVLink communication between the Raspberry Pi and flight controller. After 61 bench trials, stable motor
response and reliable MAVLink link were confirmed.

4.2  Flight Testing
Initial outdoor tests at BUET campus were conducted at 3 m altitude over the central lawn. The first seven
attempts failed due to GPS lock timeout and vibration-induced IMU drift. After adding vibration damping
foam mounts under the flight controller and tuning the PID roll/pitch gains, stable hover and waypoint-
following were achieved.
The Sylhet field trial was conducted over Gutibari Plantation. The lawnmower mission was uploaded and
the drone executed 22 survey strips autonomously, capturing footage for post-processing. The targeted
anomaly flight was also demonstrated, navigating to a manually flagged coordinate and returning to launch.





                                    Figure: Autonomous Flight — Captured During Survey





                          UAV-Based Vegetation Stress Mapping for Tea Garden  · Group 2  · Page 20

## Original report — page 21

4.3 Software Pipeline Execution
The Python pipeline was executed on a laptop post-flight. Processing a 3-minute flight video (approx. 5,400
frames at 30 fps, with 1-in-30 frame sampling yielding 180 frames) took approximately 45 seconds for
frame extraction, 2 minutes for EXIF generation, and 3 minutes for mosaic and heatmap generation on an
Intel Core i7 CPU.
The SegFormer inference pipeline was executed on Google Colab during training and evaluation. For the
final deployment demo, a quantised ONNX version was tested on the Raspberry Pi, achieving approximately
2.1 seconds per image inference time.





                          UAV-Based Vegetation Stress Mapping for Tea Garden  · Group 2  · Page 21

## Original report — page 22

5 Design Analysis and Evaluation

5.1 Novelty
The proposed system is, to our knowledge, the first to integrate: (i) dual-index RGB vegetation analysis (ExG
+ VARI) with  (ii) a transformer-based segmentation model (SegFormer)  in  (iii) a  fully closed-loop
autonomous UAV pipeline specifically targeted at tea garden disease detection in the Bangladesh context.
The use of synthetic GPS tagging to enable geo-referenced mapping from standard video (without GPS-
enabled camera hardware) is also a novel practical contribution.

5.2 Design Considerations (PO-c)

5.2.1  Public Health and Safety
UAV operations were conducted strictly within BCAA guidelines — below 120 m AGL, within visual line of
sight, with a dedicated observer at  all times. An emergency kill-switch was maintained by the pilot
throughout every flight. The system's early disease detection capability directly supports public health by
enabling timely, targeted pesticide application, reducing chemical runoff into water supplies compared to
preventive blanket spraying.

5.2.2 Environmental Considerations
Targeted application of fungicides and pesticides guided by the system's disease maps can reduce chemical
usage by an estimated 30–60% compared to full-field prophylactic treatment (based on published precision
agriculture studies). This benefits local biodiversity, reduces soil acidification, and lowers downstream
water contamination.

5.2.3  Cultural and Societal Needs
Bangladesh's tea industry employs over 100,000 workers, many of whom are from indigenous communities.
The system provides actionable, GPS-located disease alerts accessible via a simple GUI, empowering
plantation managers with minimal technical background. Reduced crop loss translates directly to improved
worker livelihoods and food security in tea-dependent communities.

5.3  Investigations (PO-d)

5.3.1 Design of Experiment
Vegetation mapping was qualitatively validated by comparing generated ExG/VARI maps against visually
identified stressed patches (yellowing, browning) observed on the BUET campus lawn. The deep learning
model was quantitatively evaluated on a held-out test set of 792 images unseen during training.

5.3.2 Data Collection
Aerial video for vegetation mapping was collected during BUET campus and Sylhet field flights. The tea leaf
classification dataset (1,158 annotated images, 7 classes) was sourced from an open agricultural computer
vision  repository on  Roboflow.  Synthetic GPS  trajectories were  generated  programmatically  for
demonstration.




                          UAV-Based Vegetation Stress Mapping for Tea Garden  · Group 2  · Page 22

## Original report — page 23

5.3.3  Results and Analysis
Segmentation performance on the held-out test set:

           Metric                  Value                             Interpretation

Pixel Accuracy                       0.977              Excellent — 97.7% of pixels correctly classified

Average Dice Score                  0.685              Good — limited by algal leaf spot class

Brown Blight Dice                    0.797               Good spatial localisation of lesions

Grey Blight Dice                     0.798               Good spatial localisation of lesions

Algal Leaf Spot Dice                  0.460              Weaker — small, irregular lesion shapes

                                      Table 7: Segmentation evaluation metrics


       Disease Class               Precision             Recall            F1-Score          Samples

Tea Algal Leaf Spot                  0.844             0.871             0.857             62

Brown Blight                       0.862             0.737             0.794             76

Gray Blight                         0.918             0.954             0.936             152

Helopeltis                          0.956             0.945             0.950             91

Red Spider Mite                     0.913             0.948             0.930             77

Green Mirid Bug                    0.959             0.969             0.964             193

Healthy Leaf                        0.979             0.972             0.975             141

Weighted Average                  0.931             0.932             0.931             792
                    Table 8: Per-class classification report (792 test samples, loss = 0.371, acc = 0.932)





                          UAV-Based Vegetation Stress Mapping for Tea Garden  · Group 2  · Page 23

## Original report — page 24

Figure: Sample Predicted Segmentation Masks vs. Ground Truth — Six Disease Examples

5.3.4  Interpretation and Conclusions
Grey blight and healthy leaf classes achieve Dice > 0.79 and F1 > 0.93, confirming strong model
performance on the dominant classes. The lower Dice score (0.46) for algal leaf spot is expected given the
small, irregular morphology of algal lesions and comparatively fewer training samples (62 test instances vs.
193 for green mirid bug). Weighted average F1 of 0.931 confirms that the model is production-ready for the
majority of disease classes. ExG and VARI maps visually corresponded to known stressed regions in both the
BUET lawn and Sylhet field trials.

5.4  Limitations of Tools (PO-e)
Several limitations were identified during the project:
   •  GPS integration gap: The onboard camera does not natively produce GPS-tagged images,
        necessitating the synthetic GPS workaround. This limits absolute geo-referencing accuracy.
   •  Raspberry Pi inference speed: Full SegFormer-B2 inference runs at ~2.1 s/image on Raspberry Pi 4,
       making true real-time classification infeasible without model optimisation.
   •  Weather sensitivity: The drone cannot fly in rain or wind above Beaufort scale 3, limiting
        operational windows.
   •   Limited flight endurance: ~12 minutes per battery set constrains survey coverage per sortie.
   •   Mission Planner dependency: Auto-mission generation for anomaly flights still requires a laptop
       connection; a fully embedded solution requires further software integration.





                          UAV-Based Vegetation Stress Mapping for Tea Garden  · Group 2  · Page 24

## Original report — page 25

5.5 Impact Assessment (PO-f)

5.5.1  Societal and Cultural Impact
Automated disease surveillance democratises precision agriculture  for smallholder and community-
managed tea estates that cannot afford agronomist visits. Alert reports delivered to plantation managers
via a mobile interface can directly prevent crop loss events that would otherwise devastate seasonal
worker wages.

5.5.2 Health and Safety Impact
Reducing blanket pesticide use lowers chemical exposure for estate workers and reduces food-safety
concerns in harvested tea. UAV operation itself was managed with all required safety protocols; no injuries
occurred during testing.

5.5.3  Legal Impact
Drone flights were conducted with landowner consent and within permitted altitude limits. Data collected
was used exclusively for vegetation analysis and was not shared commercially. All relevant BCAA drone
operation regulations were followed.

5.6  Sustainability Evaluation (PO-g)
Economic sustainability: The BDT 50,000 prototype cost is achievable for established tea estates and
agricultural cooperatives, and projected to reduce to BDT 30,000–35,000 at production scale. A single
prevented disease outbreak affecting 10% of a 10-hectare estate could represent BDT 200,000+ in saved
crop value, yielding strong ROI.
Environmental sustainability: Targeted pesticide application reduces chemical runoff and soil acidification.
Low-energy UAV surveys (12 min flight, ~250 Wh/session) have negligible carbon footprint compared to
vehicle-based manual inspection.
Technical sustainability: The modular software architecture allows easy update of the deep learning model
as new disease classes or improved architectures become available, without requiring hardware changes.

5.7  Ethical Issues (PO-h)
Aerial surveillance of agricultural and private land raises privacy considerations. The system captures
imagery exclusively for vegetation analysis; no images of individuals are retained or transmitted. Plantation
surveys are conducted with explicit informed consent from landowners. The team commits to transparent
data handling practices in any commercial deployment.





                          UAV-Based Vegetation Stress Mapping for Tea Garden  · Group 2  · Page 25

## Original report — page 28

7 Communication to External Stakeholders (PO-j)

7.1  Executive Summary

For Tea Garden Managers and Agricultural Officers
We have built a low-cost drone system that automatically scans your tea garden every day and
shows you exactly where disease is starting — before it spreads.

HOW IT WORKS: The drone flies over the garden on its own, takes pictures, and creates a colour
map showing which areas of the garden look stressed (yellow/red = problem zones, green =
healthy). If a problem zone is found, the drone automatically flies back for a close-up photo, and our
AI software tells you which disease is present: algal leaf spot, brown blight, or grey blight — with
over 93% accuracy.

WHAT YOU NEED: One drone (~BDT 50,000 one-time cost), a laptop, and a person to press "Start
Mission" each morning. No drone piloting experience required after setup.

RESULT: Early treatment of only the affected zone instead of the whole garden — saving on
pesticide cost and protecting worker health.


7.2 User Manual (Quick-Start Guide)
    1.  Power on the drone and ensure the Raspberry Pi companion computer has booted (LED indicator
         solid green).
    2.  Connect your laptop to Mission Planner via USB telemetry link.
    3.  Upload the pre-configured survey mission file for your plantation area. Verify home position GPS
         lock.
    4.  Press ARM and then AUTO MODE in Mission Planner. Stand clear of the drone.
    5.  After the mission completes and the drone lands, transfer the flight video from the Raspberry Pi SD
       card to your laptop.
    6.  Run: python process_flight.py --video <file.mp4> --ref_lat <latitude> --ref_lon <longitude>
    7.  Open the generated heatmap image. Red zones indicate potential disease. Note the flagged GPS
        coordinates.
    8.   If anomaly detected, upload the auto-generated anomaly_mission.waypoints file to Mission
       Planner and fly.
    9.  After close-up image acquisition, run: python classify_disease.py --image <close_up.jpg>
    10. The terminal will output the detected disease class and severity estimate. Consult your agronomist
        for treatment.




                          UAV-Based Vegetation Stress Mapping for Tea Garden  · Group 2  · Page 28

## Original report — page 29

8  Project Management and Cost Analysis (PO-k)

8.1  Bill of Materials
         Component              Qty        Unit Cost (BDT)                   Total (BDT)

F450 Quadcopter Frame              1             3,500                         3,500

A2212 1000KV Brushless Motor        4             1,000                         4,000

30A SimonK ESC                     4             800                         3,200

Pixhawk-compatible Flight                                  1             8,000                         8,000Controller

Raspberry Pi 4 (2 GB)                 1             7,500                         7,500

Samsung S860 RGB Camera            1             2,000                         2,000

3S 5,200 mAh LiPo Battery             2             3,000                         6,000

10×4.5 Propellers (pairs)              4             200                        800

u-blox M8N GPS Module              1             3,500                         3,500

Frame accessories, wiring,                   —       —                          4,000connectors

Crash repairs and replacement                   —       —                          7,500parts

TOTAL                                                                        ~50,000

                                          Table 11: Detailed bill of materials


8.2 Prototype Unit Cost
Total prototype cost: approximately BDT 50,000 (≈USD 455 at current exchange rates). This is 4–20×
cheaper than commercially available agricultural UAV platforms. The largest single cost driver is the flight
controller (BDT 8,000), which could be replaced with a lower-cost open-source variant for mass production.

8.3 Mass-Produced Unit Cost Estimate
         Scenario                 Per-Unit Cost (BDT)                        Notes

Prototype (1 unit)                      ~50,000              Crash repairs and one-off sourcing included

                                                                  Bulk component discounts, no crashSmall batch (10–50 units)                ~38,000                                                                           contingency

Mass production (100+                                  ~30,000–32,000         PCB integration, injection-moulded housingunits)

                             Table 12: Projected per-unit cost at different production scales




                          UAV-Based Vegetation Stress Mapping for Tea Garden  · Group 2  · Page 29

## Original report — page 30

9 Future Work (PO-l)
The following improvements are identified as high-priority directions for extending this work:


  Priority              Enhancement                              Expected Impact

                 Real GPS integration via ArduPilotHigh                                                   Accurate geo-referencing without synthetic GPS                      camera trigger

              Edge-optimised SegFormer (TensorRT /High                                                    Real-time inference on Raspberry Pi (<0.5 s/image)                       ONNX)

             Automated spray module triggered byHigh                                                                   Fully closed-loop treatment pipeline                           disease GPS

                 Multispectral NIR band addition forMedium                                         More robust vegetation stress detection                         NDVI

                Mobile app for agronomist alertMedium                                                     Accessible disease reports for field managers                               delivery

Medium      Expand to 10+ disease and pest classes         Broader applicability across tea diseases

                 Solar-powered Raspberry Pi forLow                                             Reduce operational dependency on battery swaps                    extended deployment

                 Cloud-based aggregated diseaseLow                                                       Regional surveillance at estate network level                    mapping dashboard
                                      Table 13: Prioritised future enhancements





                          UAV-Based Vegetation Stress Mapping for Tea Garden  · Group 2  · Page 30

## Original report — page 31

10 References

[1]  E. Xie, W. Wang, Z. Yu, A. Anandkumar, J. M. Alvarez, and P. Luo, "SegFormer: Simple and Efficient
Design for Semantic Segmentation with Transformers," in Advances in Neural Information Processing
Systems (NeurIPS), 2021, vol. 34, pp. 12077–12090.
[2]  D. M. Woebbecke, G. E. Meyer, K. Von Bargen, and D. A. Mortensen, "Color indices for weed
identification under various soil, residue, and lighting conditions," Transactions of the ASAE, vol. 38, no. 1,
pp. 259–269, 1995.
[3]  A. A. Gitelson, Y. J. Kaufman, R. Stark, and D. Rundquist, "Novel algorithms for remote estimation of
vegetation fraction," Remote Sensing of Environment, vol. 80, no. 1, pp. 76–87, 2002.
[4]     ArduPilot  Development  Team,   "ArduPilot  Documentation,"  2024.   [Online].   Available:
https://ardupilot.org/
[5] Roboflow, "Tea Leaf Disease Segmentation Dataset," 2023. [Online]. Available: https://roboflow.com
[6]   Raspberry  Pi Foundation, "Raspberry  Pi 4 Model B Product  Brief," 2023.  [Online].  Available:
https://www.raspberrypi.com/products/raspberry-pi-4-model-b/
[7] K. He, X. Zhang, S. Ren, and J. Sun, "Deep Residual Learning for Image Recognition," in Proc. IEEE CVPR,
2016, pp. 770–778.
[8] M. Tan and Q. V. Le, "EfficientNet: Rethinking Model Scaling for Convolutional Neural Networks," in
Proc. ICML, 2019.
[9] Bangladesh Civil Aviation Authority (CAAB), "Unmanned Aircraft System (UAS) Regulations," 2020.





                          UAV-Based Vegetation Stress Mapping for Tea Garden  · Group 2  · Page 31
