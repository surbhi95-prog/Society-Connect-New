function showServiceDetails(id) {
    const s = servicesData[id];
    if (!s) return;

    document.getElementById("serviceDetails").innerHTML = `
        <div class="service-detail-header">
            <i class="fa-solid ${s.icon}"></i>
            <h2>${s.name}</h2>
            <p>${s.provider}</p>
        </div>

        <div class="info-row">
            <i class="fa-solid fa-phone"></i>
            <div>${s.contact}</div>
        </div>

        ${s.email ? `
        <div class="info-row">
            <i class="fa-solid fa-envelope"></i>
            <div>${s.email}</div>
        </div>` : ""}

        ${s.description ? `
        <div class="info-row">
            <i class="fa-solid fa-info-circle"></i>
            <div>${s.description}</div>
        </div>` : ""}

        <div class="contact-actions">
            <button class="action-btn call-btn" onclick="location.href='tel:${s.contact}'">
                Call Now
            </button>
            ${s.email ? `
            <button class="action-btn email-btn" onclick="location.href='mailto:${s.email}'">
                Send Email
            </button>` : ""}
        </div>
    `;

    document.getElementById("serviceModal").style.display = "flex";
    document.getElementById("pageContent").classList.add("blur-background");
}

function closeModal() {
    document.getElementById("serviceModal").style.display = "none";
    document.getElementById("pageContent").classList.remove("blur-background");
}

function outsideClick(e) {
    if (e.target.id === "serviceModal") {
        closeModal();
    }
}
