// Madras Foodies Consultancy - Client Script

document.addEventListener("DOMContentLoaded", () => {
  // 1. Mobile Navigation Toggle
  const toggle = document.querySelector(".menu-toggle");
  const nav = document.querySelector(".nav");

  if (toggle && nav) {
    toggle.addEventListener("click", (e) => {
      e.stopPropagation();
      nav.classList.toggle("open");
      const isOpen = nav.classList.contains("open");
      toggle.setAttribute("aria-expanded", isOpen);
    });

    document.addEventListener("click", (e) => {
      if (!nav.contains(e.target) && !toggle.contains(e.target)) {
        nav.classList.remove("open");
        toggle.setAttribute("aria-expanded", "false");
      }
    });

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && nav.classList.contains("open")) {
        nav.classList.remove("open");
        toggle.setAttribute("aria-expanded", "false");
      }
    });
  }

  // 2. Tab Switcher for Contact Page Forms (Contact, Client, Restaurant)
  const tabButtons = document.querySelectorAll(".form-tab-btn");
  const formPanels = document.querySelectorAll(".form-panel");

  if (tabButtons.length > 0) {
    tabButtons.forEach((btn) => {
      btn.addEventListener("click", () => {
        const targetFormId = btn.getAttribute("data-form");

        tabButtons.forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");

        formPanels.forEach((panel) => {
          if (panel.id === targetFormId) {
            panel.style.display = "block";
            panel.classList.add("active-panel");
          } else {
            panel.style.display = "none";
            panel.classList.remove("active-panel");
          }
        });
      });
    });
  }

  // 3. Multi-Member Review Carousel Slider Navigation
  const slides = document.querySelectorAll(".review-slide");
  const dots = document.querySelectorAll(".carousel-dots .dot");
  const counter = document.querySelector("#carouselCounter");
  const prevBtn = document.querySelector("#prevReviewBtn");
  const nextBtn = document.querySelector("#nextReviewBtn");
  const jumpBtn = document.querySelector("#jumpToReviewBtn");

  let currentSlide = 0;
  const totalSlides = slides.length;

  function showSlide(index) {
    if (totalSlides === 0) return;
    currentSlide = (index + totalSlides) % totalSlides;

    slides.forEach((s, i) => {
      s.classList.toggle("active-slide", i === currentSlide);
    });

    dots.forEach((d, i) => {
      d.classList.toggle("active", i === currentSlide);
    });

    if (counter) {
      if (currentSlide === totalSlides - 1) {
        counter.textContent = `Slide ${currentSlide + 1} of ${totalSlides} (⭐ Member Review Option)`;
      } else {
        counter.textContent = `Slide ${currentSlide + 1} of ${totalSlides}`;
      }
    }
  }

  if (prevBtn) {
    prevBtn.addEventListener("click", () => showSlide(currentSlide - 1));
  }
  if (nextBtn) {
    nextBtn.addEventListener("click", () => showSlide(currentSlide + 1));
  }
  if (jumpBtn) {
    jumpBtn.addEventListener("click", () => {
      showSlide(totalSlides - 1);
      const lastSlide = document.querySelector(".last-slide-review-option");
      if (lastSlide) {
        lastSlide.scrollIntoView({ behavior: "smooth", block: "center" });
      }
    });
  }

  dots.forEach((dot, i) => {
    dot.addEventListener("click", () => showSlide(i));
  });


  // 4. Generic Form Submission Engine with Double-Click Protection
  function setupAjaxForm(formSelector, endpoint, messageSelector) {
    const form = document.querySelector(formSelector);
    if (!form) return;

    form.addEventListener("submit", async (e) => {
      e.preventDefault();

      const messageEl = document.querySelector(messageSelector) || form.querySelector(".form-feedback");
      const submitBtn = form.querySelector(".submit-btn");
      const btnText = submitBtn?.querySelector(".btn-text");
      const btnSpinner = submitBtn?.querySelector(".btn-spinner");

      // Reset feedback display
      if (messageEl) {
        messageEl.className = "form-feedback";
        messageEl.textContent = "";
        messageEl.style.display = "none";
      }

      // Prevent duplicate submissions: disable submit button
      if (submitBtn) submitBtn.disabled = true;
      if (btnText) btnText.style.display = "none";
      if (btnSpinner) btnSpinner.style.display = "inline";

      const formData = new FormData(form);
      const payload = Object.fromEntries(formData.entries());

      try {
        const response = await fetch(endpoint, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Accept": "application/json"
          },
          body: JSON.stringify(payload)
        });

        const result = await response.json();
        const isSuccess = response.ok && (result.success === true || result.ok === true);

        if (messageEl) {
          messageEl.textContent = result.message || (isSuccess ? "Data saved successfully" : "Failed to save data");
          messageEl.className = `form-feedback ${isSuccess ? "success" : "error"}`;
          messageEl.style.display = "block";
        }

        // Only clear the form if saving succeeded
        if (isSuccess) {
          form.reset();
        }
      } catch (err) {
        if (messageEl) {
          messageEl.textContent = "Could not connect to the server. Please check your connection and try again.";
          messageEl.className = "form-feedback error";
          messageEl.style.display = "block";
        }
      } finally {
        // Re-enable button after request finishes
        if (submitBtn) submitBtn.disabled = false;
        if (btnText) btnText.style.display = "inline";
        if (btnSpinner) btnSpinner.style.display = "none";
      }
    });
  }

  // Connect all 4 forms to their respective backend API endpoints
  setupAjaxForm("#contactForm", "/api/contacts", "#contactFormMessage");
  setupAjaxForm("#clientForm", "/api/clients", "#clientFormMessage");
  setupAjaxForm("#restaurantForm", "/api/restaurants", "#restaurantFormMessage");
  setupAjaxForm("#reviewForm", "/api/reviews", "#reviewFormMessage");
});
