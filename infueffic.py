import streamlit as st
from PIL import Image
import numpy as np
import tempfile
import cv2
import os
import base64

def apply_effects(image, effect):
    if effect == "Dwarf":
        return image.resize((int(image.width), int(image.height / 2)))
    elif effect == "Giant":
        return image.resize((int(image.width), int(image.height * 2)))
    elif effect == "Grayscale Background":
        # Convert image to grayscale
        gray_image = np.array(image.convert("L"))
        # Copy the grayscale image to all three channels
        result = np.stack((gray_image,) * 3, axis=-1)
        return Image.fromarray(result)
    elif effect == "Fire Background":
        fire_image = np.array(image)
        fire_overlay = np.full(fire_image.shape, [255, 0, 0], dtype=np.uint8)  # Fire color
        blended = cv2.addWeighted(fire_image, 0.7, fire_overlay, 0.3, 0)
        return Image.fromarray(blended)
    elif effect == "Ice Background":
        ice_image = np.array(image)
        ice_overlay = np.full(ice_image.shape, [173, 216, 230], dtype=np.uint8)  # Ice color
        blended = cv2.addWeighted(ice_image, 0.7, ice_overlay, 0.3, 0)
        return Image.fromarray(blended)
    return image

def get_download_link(file_path, file_name):
    """Generate a download link for a file"""
    with open(file_path, 'rb') as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    href = f'<a href="data:video/mp4;base64,{b64}" download="{file_name}">Download Processed Video</a>'
    return href

st.title("Video Effects Application")

uploaded_file = st.file_uploader("Choose a video file", type=["mp4", "mov"])

if uploaded_file is not None:
    # Save the uploaded file temporarily
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_file.read())
    
    # Open the video using the temporary path
    video_capture = cv2.VideoCapture(tfile.name)
    
    if not video_capture.isOpened():
        st.error("Failed to open the video.")
    else:
        effect = st.selectbox("Choose Effect", ["Dwarf", "Giant", "Grayscale Background", "Fire Background", "Ice Background"])
        fps = video_capture.get(cv2.CAP_PROP_FPS)
        
        if st.button("Apply Effect"):
            with st.spinner("Processing video..."):
                frames = []
                while True:
                    ret, frame = video_capture.read()
                    if not ret:
                        break
                    
                    # Convert frame to RGB format
                    image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    
                    # Apply the effect
                    processed_image = apply_effects(image, effect)
                    
                    # Add the processed frame to the list
                    frames.append(np.array(processed_image))
                
                # Close the original video
                video_capture.release()
                
                if frames:
                    # Save the processed video
                    output_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
                    
                    # Get the dimensions of the processed frame
                    height, width = frames[0].shape[:2]
                    
                    # Create video writer
                    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                    out = cv2.VideoWriter(output_file.name, fourcc, fps if fps > 0 else 20.0, (width, height))
                    
                    # Write frames
                    for frame in frames:
                        # Make sure the frame is in BGR format before writing
                        out.write(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
                    
                    # Close the video writer
                    out.release()
                    
                    # Display the processed video
                    st.video(output_file.name)
                    
                    # Create a download button
                    download_filename = f"processed_{uploaded_file.name}" if hasattr(uploaded_file, 'name') else "processed_video.mp4"
                    st.markdown(get_download_link(output_file.name, download_filename), unsafe_allow_html=True)
                else:
                    st.error("No frames were captured from the video.")
    
    # Delete the temporary file
    os.unlink(tfile.name)





    hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            .stDeployButton {display:none;}
            #stStreamlitLogo {display: none;}
            a {
                text-decoration: none;
                color: inherit;
                pointer-events: none;
            }
            a:hover {
                text-decoration: none;
                color: inherit;
                cursor: default;
            }
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
