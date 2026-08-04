
  /* ---------- Efeitos do site ---------- */
  function iniciarSite() {
    // Sombra da navbar ao rolar
    const nav = document.querySelector(".navbar-fama");
    if (nav) {
      const aoRolar = () => nav.classList.toggle("rolada", window.scrollY > 10);
      aoRolar();
      window.addEventListener("scroll", aoRolar, { passive: true });
    }
    // Revelação ao rolar
    const alvos = document.querySelectorAll(".revelar");
    if (alvos.length && "IntersectionObserver" in window) {
      const obs = new IntersectionObserver((entradas) => {
        entradas.forEach((e) => {
          if (e.isIntersecting) {
            e.target.classList.add("visivel");
            obs.unobserve(e.target);
          }
        });
      }, { threshold: 0.14 });
      alvos.forEach((el) => obs.observe(el));
    } else {
      alvos.forEach((el) => el.classList.add("visivel"));
    }
    // Ano automático no rodapé
    document.querySelectorAll("[data-ano]").forEach((el) => (el.textContent = new Date().getFullYear()));
  }

  /* ---------- Olhinho de senha ---------- */
  function iniciarVerSenha(raiz = document) {
    raiz.querySelectorAll(".ver-senha").forEach((btn) => {
      if (btn.dataset.ok) return;
      btn.dataset.ok = "1";
      btn.addEventListener("click", () => {
        const campo = btn.parentElement.querySelector("input");
        const mostrar = campo.type === "password";
        campo.type = mostrar ? "text" : "password";
        btn.innerHTML = `<i class="bi ${mostrar ? "bi-eye-slash" : "bi-eye"}"></i>`;
        btn.setAttribute("aria-label", mostrar ? "Ocultar senha" : "Mostrar senha");
      });
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    iniciarVerSenha();
    iniciarSite();
  });

  return {
    iniciarVerSenha
  };
