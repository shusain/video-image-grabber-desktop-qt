# Frame Extractor
 
https://user-images.githubusercontent.com/523230/234333718-81961446-0478-4063-8da4-2f20db198310.mp4

This application allows users to load a video, control playback (frame-by-frame, scrubbing, play/pause), and export individual frames as images.

## Requirements

- Python 3.7 or later
- Native video codecs installed so the QT Media Player can decode/playback the video and extract frames: https://www.codecguide.com/download_kl.htm (the basic package is likely enough, pay attention during install to avoid extra software)
- PyQt5 (installed from requirements.txt below)

## Installation

1. Clone the repository:

    ```
    git clone https://github.com/yourusername/frame_extractor.git
    cd frame_extractor
    ```

1.  Create a virtual environment and activate it:

    ```
    python -m venv venv
    source venv/bin/activate # Linux/macOS
    venv\Scripts\activate # Windows
    ```

1. Install the required dependencies:
    ```
    pip install -r requirements.txt
    ```

## Usage

1. Run the application:
    ```
    python main.py
    ```

2. Load a video file by clicking the "Open" button.

3. Control the video playback using the play/pause button, slider, and next frame button.

4. Click the "Export Frame" button to save the current frame as an image.

5. The exported frames will be saved in the "output" folder within the project directory.

### Instant-NGP
To use the output from this program as input for colmap and subsequent instant-ngp processing assuming you have instant-ngp installed you can run

```
python C:\Users\shaun\Development\instant-ngp\scripts\colmap2nerf.py --images ./output --run_colmap --aabb_scale 64
```

This will generate a transforms.json file in the current working directory that you can drag and drop onto the instant-ngp UI (launch separately) to start training of a NeRF model.

Once  the model is generated you can create a set of camera paths within instant-ngp, save out the camera positions as JSON, and save the ingp file (model snapshot) to disk and then run a command similar to the following to process the model and JSON into a video output as seen above:

```
py -3.9 C:\Users\shaun\Development\instant-ngp\scripts\run.py --load_snapshot=construction.ingp --video_camera_path=construction2_cam.json --video_n_seconds=10
```