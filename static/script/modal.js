// -------------- LOAD "MY COLLECTION" --------------
document.getElementById("collectionLink").addEventListener("click", (e) => {
  e.preventDefault();
  document.getElementById("collectionSection").style.display = "block";
  document.querySelector(".home").style.display = "none";
  loadMyCollection();
});

// -------------- LOAD "HOME" --------------
document.getElementById("homeLink").addEventListener("click", (e) => {
  e.preventDefault();
  document.getElementById("collectionSection").style.display = "none";
  document.querySelector(".home").style.display = "flex";
});

// -------------- LOAD TOP 5 SONGS --------------
window.addEventListener('DOMContentLoaded', () => {
  loadTopSongs();
});


// -------------- LOAD TOP 5 SONGS --------------
async function loadTopSongs() {
  try {
    let response = await fetch('/top-songs');
    if (!response.ok) throw new Error(`Status ${response.status}`);
    let topSongs = await response.json();

    const container = document.getElementById("topSongsContainer");
    container.innerHTML = "";

    topSongs.forEach(song => {
      const item = document.createElement("div");
      item.className = "top-song-item";
      item.innerHTML = `
        <span>${song.name} - ${song.artist} (${song.likes} likes)</span>
        <button class="add-btn">+</button>
      `;
      // Add click event
      item.querySelector('.add-btn').addEventListener('click', () => {
        addToCollection(song);
      });
      container.appendChild(item);
    });
  } catch (err) {
    console.error("Error loading top songs:", err);
  }
}

// -------------- SEARCH --------------
async function performSearch() {
  const container = document.getElementById("searchResults");
  container.innerHTML = "";

  const search = document.getElementById("search").value.trim();
  if (!search) return;

  try {
    const response = await fetch(`/search?search=${search}`);
    if (!response.ok) {
      throw new Error(`Error: HTTP ${response.status}`);
    }

    const results = await response.json();

    // If no results
    if (!results || results.length === 0) {
      container.innerHTML = "<p>No results found.</p>";
      return;
    }

    // Display each result
    results.forEach(song => {
      const div = document.createElement("div");
      div.className = "top-song-item";
      // Make the text color white
      div.style.color = "white";

      div.innerHTML = `
        <span>${song.name} - ${song.artist} (${song.likes} likes)</span>
        <button class="add-btn">+</button>
      `;
      // Add "click" listener to the + button
      div.querySelector('.add-btn').addEventListener('click', () => {
        addToCollection(song);
      });
      container.appendChild(div);
    });
  } catch (err) {
    console.error("Search error:", err);
  }
}


// -------------- ADD TO COLLECTION --------------
async function addToCollection(song) {
  try {
    let response = await fetch('/add-to-collection', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(song)
    });
    let result = await response.json();
    alert(result.message || "Song added!");
  } catch (err) {
    console.error("Error adding to collection:", err);
  }
}

// -------------- LOAD "MY COLLECTION" --------------
async function loadMyCollection() {
  const container = document.getElementById("collectionContainer");
  container.innerHTML = "";

  try {
    const response = await fetch('/my-collection');
    const songs = await response.json();

    if (!songs.length) {
      container.innerHTML = "<p>Your collection is empty.</p>";
      return;
    }

    songs.forEach(song => {
      const div = document.createElement("div");
      div.className = "top-song-item";
      div.innerHTML = `
        <span>${song.name} - ${song.artist} (${song.genre})</span>
        <button class="add-btn">Remove</button>
      `;
      div.querySelector('.add-btn').addEventListener('click', () => {
        removeFromCollection(song.id);
      });
      container.appendChild(div);
    });
  } catch (err) {
    console.error("Failed to load collection:", err);
  }
}

async function removeFromCollection(songId) {
  try {
    await fetch('/remove-from-collection', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: songId })
    });
    loadMyCollection(); // refresh view
  } catch (err) {
    console.error("Error removing song:", err);
  }
}
