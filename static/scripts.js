async function applyChanges() {
    const command = document.getElementById("command").value.trim();

    if (!command) {
        alert("Command cannot be empty.");
        return;
    }

    // Determine the change type based on command content
    const isCSS = command.startsWith("/*") || command.includes("{");
    const changeType = isCSS ? "css" : "js";

    try {
        const response = await fetch("https://alwen.up.railway.app/apply-changes/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-Change-Type": changeType, // Specify the type (css or js)
            },
            body: JSON.stringify({ command }),
        });

        if (response.ok) {
            const data = await response.json();

            if (changeType === "css") {
                // Apply CSS dynamically
                let styleTag = document.getElementById("dynamic-style");
                if (!styleTag) {
                    styleTag = document.createElement("style");
                    styleTag.id = "dynamic-style";
                    document.head.appendChild(styleTag);
                }
                styleTag.innerHTML = data.css; // Apply generated CSS
            } else {
                // Apply JavaScript dynamically
                let scriptTag = document.getElementById("dynamic-script");
                if (scriptTag) {
                    scriptTag.remove(); // Remove old script to avoid conflicts
                }

                scriptTag = document.createElement("script");
                scriptTag.id = "dynamic-script";
                scriptTag.textContent = data.js; // Apply generated JS
                document.body.appendChild(scriptTag);
            }

            alert(`${changeType.toUpperCase()} applied successfully.`);
        } else {
            const errorData = await response.json();
            alert(`Failed to apply ${changeType.toUpperCase()}: ${errorData.detail}`);
        }
    } catch (error) {
        console.error(`Error applying ${changeType.toUpperCase()}:`, error);
        alert(`An error occurred while applying ${changeType.toUpperCase()}. Check the console for details.`);
    }
}


document.getElementById("scrollToFooter").addEventListener("click", function (e) {
    e.preventDefault(); // Prevent default link behavior
    document.getElementById("footer").scrollIntoView({
      behavior: "smooth", // Enables smooth scrolling
      block: "start", // Scrolls to the top of the footer section
    });
  });

  document.querySelectorAll(".nav-link").forEach((link) => {
    link.addEventListener("click", (e) => {
      e.preventDefault(); // Prevent default anchor behavior
      const targetId = link.getAttribute("href").substring(1); // Remove the '#' from href
      const targetElement = document.getElementById(targetId);
  
      if (targetElement) {
        targetElement.scrollIntoView({
          behavior: "smooth", // Smooth scrolling animation
          block: "start", // Aligns to the top of the section
        });
      }
    });
  });
  

  document.querySelectorAll('[data-dial-toggle]').forEach((toggle) => {
    toggle.addEventListener('click', () => {
        const menu = document.getElementById(toggle.getAttribute('aria-controls'));
        menu.classList.toggle('hidden');
        const expanded = toggle.getAttribute('aria-expanded') === 'true';
        toggle.setAttribute('aria-expanded', !expanded);
    });
});


async function fetchAnimeGif() {
    const container = document.getElementById("animeGifContainer");
    const btn = document.getElementById("generateAnimeBtn");
    btn.disabled = true;
    btn.textContent = "Loading...";

    try {
      const response = await fetch("https://alwen.up.railway.app/anime-of-the-day");
      if (response.ok) {
        const data = await response.json();
        if (data.gif_url) {
          container.innerHTML = `<img src="${data.gif_url}" alt="Anime GIF" class="max-w-full rounded-lg shadow-lg">`;
        } else {
          container.innerHTML = `<p class="text-red-500">No GIFs found. Try again.</p>`;
        }
      } else {
        container.innerHTML = `<p class="text-red-500">Failed to fetch GIF. Please try again later.</p>`;
      }
    } catch (error) {
      container.innerHTML = `<p class="text-red-500">Error: ${error.message}</p>`;
    } finally {
      btn.disabled = false;
      btn.textContent = "Generate";
    }
  }


  document.getElementById("generateAnimeBtn").addEventListener("click", fetchAnimeGif);

  document.getElementById("surprise").addEventListener("click", function () {
    document.getElementById("surprise").classList.add("hidden");
    document.getElementById("anime").classList.remove("hidden");
    fetchAnimeGif();
  }
    );
   
    function scrollToSection(sectionId) {
      const section = document.querySelector(sectionId);
      if (section) {
        section.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }
    document.getElementById('speed-dial-toggle').addEventListener('click', function () {
      const menu = document.getElementById('footer-speed-dial');
      
      // Toggle the hidden class for visibility
      menu.classList.toggle('hidden');
      
      // Animate the opacity and scale properties
      if (menu.classList.contains('hidden')) {
        // If the menu is hidden, reset opacity and scale
        menu.classList.remove('opacity-100', 'scale-100');
        menu.classList.add('opacity-0', 'scale-90');
      } else {
        // If the menu is visible, apply smooth transition for opacity and scale
        setTimeout(() => {
          menu.classList.remove('opacity-0', 'scale-90');
          menu.classList.add('opacity-100', 'scale-100');
        }, 10); // Delay to ensure class toggle happens after visibility change
      }
    });
    