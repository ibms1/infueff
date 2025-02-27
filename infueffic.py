import streamlit as st
from PIL import Image, ImageSequence
import numpy as np
import tempfile
import cv2
import os
import base64
from pathlib import Path
import imageio

def apply_effects(image, effect):
    if effect == "Dwarf":
        return image.resize((int(image.width), int(image.height / 2)))
    elif effect == "Giant":
        return image.resize((int(image.width), int(image.height * 2)))
    elif effect == "Grayscale Background":
        # Convert image to grayscale but keep it as RGB
        gray_image = np.array(image.convert("L"))
        result = np.stack((gray_image,) * 3, axis=-1)
        return Image.fromarray(result)
    elif effect == "Fire Background":
        fire_image = np.array(image)
        # Make sure the image is RGB
        if len(fire_image.shape) == 2 or fire_image.shape[2] < 3:
            fire_image = np.stack((fire_image,) * 3, axis=-1)
        fire_overlay = np.full(fire_image.shape, [255, 0, 0], dtype=np.uint8)  # Fire color
        blended = cv2.addWeighted(fire_image, 0.7, fire_overlay, 0.3, 0)
        return Image.fromarray(blended)
    elif effect == "Ice Background":
        ice_image = np.array(image)
        # Make sure the image is RGB
        if len(ice_image.shape) == 2 or ice_image.shape[2] < 3:
            ice_image = np.stack((ice_image,) * 3, axis=-1)
        ice_overlay = np.full(ice_image.shape, [173, 216, 230], dtype=np.uint8)  # Ice color
        blended = cv2.addWeighted(ice_image, 0.7, ice_overlay, 0.3, 0)
        return Image.fromarray(blended)
    return image

def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">Download {file_label}</a>'
    return href

# Initialize session state variables if they don't exist
if 'processed_gif_path' not in st.session_state:
    st.session_state.processed_gif_path = None

st.title("GIF Effects Application")

uploaded_file = st.file_uploader("Choose a GIF file", type=["gif"])

if uploaded_file is not None:
    # Save the uploaded file temporarily
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.gif')
    tfile.write(uploaded_file.read())
    tfile_path = tfile.name
    tfile.close()
    
    # Display the original GIF
    st.subheader("Original GIF")
    st.image(tfile_path)
    
    # Load the GIF using Pillow
    try:
        gif = Image.open(tfile_path)
        
        effect = st.selectbox("Choose Effect", ["Dwarf", "Giant", "Grayscale Background", "Fire Background", "Ice Background"])
        
        if st.button("Apply Effect"):
            with st.spinner("Processing GIF..."):
                # Get the duration of each frame
                durations = []
                for frame in ImageSequence.Iterator(gif):
                    durations.append(frame.info.get('duration', 100))
                
                # Process each frame
                frames = []
                for frame in ImageSequence.Iterator(gif):
                    # Convert frame to RGB to avoid issues with palette
                    rgb_frame = frame.convert("RGB")
                    
                    # Apply the effect
                    processed_frame = apply_effects(rgb_frame, effect)
                    
                    # Add the processed frame to the list
                    frames.append(processed_frame)
                
                if frames:
                    # Create a more permanent temporary file
                    temp_dir = Path(tempfile.gettempdir())
                    output_path = str(temp_dir / f"processed_gif_{hash(tfile_path)}.gif")
                    
                    # Save as animated GIF
                    frames[0].save(
                        output_path,
                        save_all=True,
                        append_images=frames[1:],
                        optimize=False,
                        duration=durations,
                        loop=0
                    )
                    
                    # Store the output path in session state
                    st.session_state.processed_gif_path = output_path
                else:
                    st.error("No frames were captured from the GIF.")
    except Exception as e:
        st.error(f"Error processing GIF: {e}")
    
    # Clean up the original uploaded file when done
    os.unlink(tfile_path)

# Display the processed GIF if it exists
if st.session_state.processed_gif_path and os.path.exists(st.session_state.processed_gif_path):
    st.subheader("Processed GIF")
    st.image(st.session_state.processed_gif_path)
    
    # Create download button for the processed GIF
    st.subheader("Download")
    download_filename = "processed_animation.gif"
    st.markdown(
        get_binary_file_downloader_html(st.session_state.processed_gif_path, download_filename), 
        unsafe_allow_html=True
    )
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
