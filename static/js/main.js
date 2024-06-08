const modal = document.getElementById("noteModal");
const span = document.getElementsByClassName("close")[0];

async function showNote(noteId) {
  try {
    const response = await fetch(`/note/${noteId}/`);
    const data = await response.json();

    document.getElementById("modalTitle").innerText = data.title;
    document.getElementById("modalCreated").innerText = data.created_at;
    document.getElementById("modalModified").innerText = data.modified_at;
    document.getElementById("modalContent").innerHTML = data.content;

    document.getElementById("update").href = `/note/update/${noteId}/`;
    document.getElementById("delete").href = `/note/delete/${noteId}/`;

    const tagsElement = document.getElementById("modalTags");
    tagsElement.innerText = "Tags: ";

    for (let i = 0; i < data.tags.length; i++) {
      if (i + 1 === data.tags.length) {
        tagsElement.innerText += data.tags[i].tag + ".";
        console.log(tagsElement.innerText);
      } else {
        tagsElement.innerText += data.tags[i].tag + ", ";
        console.log(tagsElement.innerText);
      }
    }

    const modal = document.getElementById("noteModal");
    modal.style.display = "flex";
  } catch (error) {
    console.error("Error fetching and displaying note:", error);
  }
}

span.onclick = function () {
  modal.style.display = "none";
};

window.onclick = function (event) {
  if (event.target == modal) {
    modal.style.display = "none";
  }
};
