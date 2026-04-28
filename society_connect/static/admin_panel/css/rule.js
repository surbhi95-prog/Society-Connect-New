function openAddModal(category = '') {
    const modal = document.getElementById('ruleModal');
    modal.style.display = 'block';   // show modal
    document.getElementById('modalTitle').innerHTML = `<i class="fa-solid fa-plus-circle"></i> Add New Rule`;
    document.getElementById('ruleForm').reset();  // clear form
    document.getElementById('ruleCategory').value = category; // pre-select category
}


function closeRuleModal() {
    document.getElementById('ruleModal').style.display = 'none';
}
