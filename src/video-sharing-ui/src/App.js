import React, { useEffect, useState } from "react";
import axios from "axios";

function App() {
  const [videos, setVideos] = useState([]);
  const [currentVideo, setCurrentVideo] = useState(null);

  useEffect(() => {
    axios
      .get("/api/videos")
      .then((response) => setVideos(response.data))
      .catch((error) => console.error("Failed to fetch videos", error));
  }, []);

  const handleVideoSelect = (video) => {
    axios
      .post("/api/videostat", { active: video.id })
      .then((response) => {
        if (response.data.success) {
          setVideos((prevVideos) =>
            prevVideos.map((v) => ({
              ...v,
              active: v.id === response.data.current,
            }))
          );
          setCurrentVideo(video);
        } else {
          console.error("Failed to update video status");
        }
      })
      .catch((error) => console.error("Error updating video status:", error));
  };

  return (
    // center
    <div className="App container mt-3" style={{ textAlign: "center" }}>
      {" "}
      {/* Use Bootstrap's container class for alignment and padding */}
      <h1 className="text-center">Video Sharing</h1> {/* Centered heading */}
      <div className="row">
        {" "}
        {/* Row to contain columns */}
        {videos.map((video) => (
          <div key={video.id} className="col-md-4 col-sm-6 mb-4">
            {" "}
            {/* Columns for each video, responsive setup */}
            <div
              className={`card ${video.active ? "border-primary" : ""}`}
              onClick={() => handleVideoSelect(video)}
            >
              <img
                src={video.thumbnail}
                alt={video.title}
                className="card-img-top"
                style={{ height: "100px" }}
              />{" "}
              {/* Use Bootstrap card image top */}
              <div className="card-body">
                <h5 className="card-title">{video.title}</h5>{" "}
                {/* Card title for video title */}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
