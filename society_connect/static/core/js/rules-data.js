const rulesData = {
    parking: {
        title: "Parking & Vehicle Management",
        rules: [
            "Only registered vehicles are allowed.",
            "No parking in emergency or fire lanes.",
            "Guest vehicles must use visitor parking.",
            "Speed limit inside society is 10 km/hr."
        ]
    },
    rental: {
        title: "Rental & Tenants",
        rules: [
            "Rental agreement must be submitted.",
            "Police verification is mandatory.",
            "Subletting is not allowed.",
            "Owner is responsible for tenant behaviour."
        ]
    },
    noise: {
        title: "Noise & Community Behaviour",
        rules: [
            "No loud music after 10 PM.",
            "Renovation allowed between 10 AM – 6 PM.",
            "Avoid loud gatherings late at night."
        ]
    },
    waste: {
        title: "Waste Management",
        rules: [
            "Segregate dry and wet waste.",
            "Dispose garbage at fixed timings.",
            "Do not litter common areas."
        ]
    },
    facility: {
        title: "Facilities Usage",
        rules: [
            "Gym timings: 6 AM – 10 PM.",
            "Clubhouse booking required.",
            "Children must be supervised."
        ]
    },
    security: {
        title: "Security & Visitors",
        rules: [
            "Visitors must register at gate.",
            "Late-night visitors require approval.",
            "Carry ID when requested."
        ]
    },
    fire: {
        title: "Fire Safety",
        rules: [
            "Do not block fire exits.",
            "Fire extinguishers must not be misused.",
            "Report fire hazards immediately."
        ]
    },
    pets: {
        title: "Pets Policy",
        rules: [
            "Pets must be leashed in common areas.",
            "Clean after your pets.",
            "Aggressive pets are not allowed."
        ]
    }
};

/* MODAL LOGIC */
const cards = document.querySelectorAll(".rule-card");
const modal = document.getElementById("rulesModal");
const modalTitle = document.getElementById("modalTitle");
const modalList = document.getElementById("modalList");
const closeBtn = document.querySelector(".close-btn");

cards.forEach(card => {
    card.addEventListener("click", () => {
        const key = card.dataset.rule;
        modalTitle.innerText = rulesData[key].title;
        modalList.innerHTML = "";

        rulesData[key].rules.forEach(rule => {
            const li = document.createElement("li");
            li.innerText = rule;
            modalList.appendChild(li);
        });

        modal.classList.add("show");
    });
});

closeBtn.addEventListener("click", () => {
    modal.classList.remove("show");
});

modal.addEventListener("click", e => {
    if (e.target === modal) modal.classList.remove("show");
});
