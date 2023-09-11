async function deletePhoto(photoId) {
  const url = getCurrentBaseURL() + "/api/photos/" + photoId;
  const accessToken = getCookie("access_token");

  try {
    const response = await fetch(url, {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });

    if (response.ok) {
      Notiflix.Notify.success("The photo has been successfully deleted.");

      location.reload();
    } else {
      Notiflix.Notify.failure(`Error when deleting a photo from ${url}`);
    }
  } catch (error) {
    Notiflix.Notify.failure("Error when deleting a photo:", error);
    Notiflix.Notify.failure("Error when deleting a photo.");
  }
}

// const homeButton = document.getElementById('home-btn').addEventListener('click', function() {
//     const homeURL = getCurrentBaseURL() + 'views/dashboard';
//     window.location.href = homeURL;
// });

const deleteButtons = document.querySelectorAll(".delete-photo-btn");
deleteButtons.forEach((button) => {
  const photoId = button.getAttribute("data-photo-id");
  button.addEventListener("click", () => deletePhoto(photoId));
});

const addPhotoButton = document.getElementById("add-photo-btn");
addPhotoButton.addEventListener("click", () => {
  $("#add-photo-modal").modal("show");
});

const uploadButton = document.getElementById("upload-button");
uploadButton.addEventListener("click", () => {
  const url = getCurrentBaseURL() + "/api/photos/upload";
  const accessToken = getCookie("access_token");

  const formData = new FormData(document.getElementById("upload-photo-form"));

  fetch(url, {
    method: "POST",
    body: formData,
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  })
    .then((response) => {
      if (response.ok) {
        Notiflix.Notify.success("Photo uploaded successfully.");
        $("#add-photo-modal").modal("hide");
      } else {
        Notiflix.Notify.failure("Error when uploading photo.");
      }
    })
    .catch((error) => {
      Notiflix.Notify.failure("Error when uploading photo:", error);
    });
});

document.getElementById("logout-btn").addEventListener("click", () => {
  const accessToken = getCookie("access_token");
  const url = getCurrentBaseURL() + "/api/auth/logout";
  fetch(url, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  })
    .then((response) => {
      if (response.ok) {
        eraseCookie("access_token");
        window.location.href = getCurrentBaseURL() + "/views/dashboard";
      } else {
        Notiflix.Notify.failure("Error logging out.");
      }
    })
    .catch((error) => {
      Notiflix.Notify.failure("Error:", error);
    });
});

/*
Update Description
*/
const updateButtons = document.querySelectorAll(".update-description-btn");

updateButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const photoId = button.getAttribute("data-photo-id");

    const modal = document.getElementById("updateDescriptionModal");
    const modalTitle = modal.querySelector(".modal-title");
    const newDescriptionInput = modal.querySelector("#newDescription");

    modalTitle.textContent = "Update Description";
    newDescriptionInput.value = "";

    const saveDescriptionBtn = modal.querySelector("#saveDescriptionBtn");
    saveDescriptionBtn.addEventListener("click", () => {
      const newDescription = newDescriptionInput.value;
      const url =
        getCurrentBaseURL() +
        `/api/photos/${photoId}?new_photo_description=${newDescriptionInput.value}`;
      const accessToken = getCookie("access_token");

      fetch(url, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`,
        },
      })
        .then((response) => {
          if (response.ok) {
            Notiflix.Notify.success("Photo updated");
            window.location.reload();
            // Close the modal window
            $("#updateDescriptionModal").modal("hide");
          } else {
            Notiflix.Notify.failure("Something wrong!");
          }
        })
        .catch((error) => {
          Notiflix.Notify.failure("Error:", error);
        });
    });

    // Open a modal window
    $("#updateDescriptionModal").modal("show");
  });
});
