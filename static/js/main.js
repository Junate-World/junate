$(document).ready(function() {
    // Add Task
    $('#addTaskForm').submit(function(e) {
        e.preventDefault();
        const site_name = $('#siteNameInput').val().trim();
        const task = $('#taskInput').val();
        const owner = $('#ownerInput').val().trim();
        const contact = $('#contactInput').val().trim();
        const phone = $('#phoneInput').val().trim();
        const summary = $('#summaryInput').val().trim();
        const project_cost = parseInt($('#projectCostInput').val(), 10);
        const execution_cost = parseInt($('#executionCostInput').val(), 10);
        if (isNaN(project_cost) || project_cost < 0 || isNaN(execution_cost) || execution_cost < 0) {
            alert('Project Cost and Execution Cost must be non-negative integers');
            return;
        }
        if (!task) {
            alert('Please select a task type');
            return;
        }
        $.ajax({
            url: '/add',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ site_name, task, owner, contact, phone, summary, project_cost, execution_cost }),
            success: function(newTask) {
                // Format created_at for display
                let createdAt = '';
                if (newTask.created_at) {
                    const d = new Date(newTask.created_at);
                    const pad = n => n.toString().padStart(2, '0');
                    createdAt = `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
                }
                // Add new card to dashboard
                const cardHtml = `<div class=\"col-md-4 mb-4 task-card\" data-id=\"${newTask.id}\">\
                    <div class=\"card\">\
                      <div class=\"card-body\">\
                        <div class=\"created-at-top\">Created: ${createdAt}</div>\
                        <h6 class=\"text-primary mb-2\"><strong>Site Name:</strong> <span class=\"editable\" contenteditable=\"true\" data-field=\"site_name\">${newTask.site_name}</span></h6>\
                        <h5 class=\"card-title\">\
                          <span class=\"badge bg-primary\">${newTask.task}</span>\
                        </h5>\
                        <p class=\"card-text mb-1\"><strong>Owner:</strong> <span class=\"editable\" contenteditable=\"true\" data-field=\"owner\">${newTask.owner}</span></p>\
                        <p class=\"card-text mb-1\"><strong>Contact Email:</strong> <span class=\"editable\" contenteditable=\"true\" data-field=\"contact\">${newTask.contact}</span></p>\
                        <p class=\"card-text mb-1\"><strong>Phone:</strong> <span class=\"editable\" contenteditable=\"true\" data-field=\"phone\">${newTask.phone}</span></p>\
                        <p class=\"card-text mb-1\"><strong>Project Cost (₦):</strong> <span class=\"editable\" contenteditable=\"true\" data-field=\"project_cost\">${newTask.project_cost ?? 0}</span></p>\
                        <p class=\"card-text mb-1\"><strong>Execution Cost (₦):</strong> <span class=\"editable\" contenteditable=\"true\" data-field=\"execution_cost\">${newTask.execution_cost ?? 0}</span></p>\
                        <p class=\"card-text mb-3 truncate-2\"><strong>Summary/Comment:</strong> <span class=\"editable\" contenteditable=\"true\" data-field=\"summary\">${newTask.summary}</span></p>\
                        <div class=\"d-flex justify-content-between align-items-center gap-2 mt-auto pt-2 border-top\">\
                          <button class=\"btn btn-sm btn-primary flex-fill save-btn\">Save</button>\
                          <button class=\"btn btn-sm btn-danger flex-fill delete-btn\">Delete</button>\
                          <a href=\"/task/${newTask.id}\" class=\"btn btn-sm btn-info flex-fill\">View</a>\
                        </div>\
                      </div>\
                    </div>\
                  </div>`;
                $('#taskCards').append(cardHtml);
                $('#addTaskForm')[0].reset();
            },
            error: function() {
                alert('Failed to add task');
            }
        });
    });

    // Delegate Save button click for dynamic cards
    $('#taskCards').on('click', '.save-btn', function() {
        const card = $(this).closest('.task-card');
        const id = card.data('id');
        const site_name = card.find('[data-field="site_name"]').text().trim();
        const task = card.find('.badge').text().trim();
        const owner = card.find('[data-field="owner"]').text().trim();
        const contact = card.find('[data-field="contact"]').text().trim();
        const phone = card.find('[data-field="phone"]').text().trim();
        const summary = card.find('[data-field="summary"]').text().trim();
        const project_cost_text = card.find('[data-field="project_cost"]').text().trim();
        const execution_cost_text = card.find('[data-field="execution_cost"]').text().trim();
        const project_cost = parseInt(project_cost_text, 10);
        const execution_cost = parseInt(execution_cost_text, 10);
        if (isNaN(project_cost) || project_cost < 0 || isNaN(execution_cost) || execution_cost < 0) {
            alert('Project Cost and Execution Cost must be non-negative integers');
            return;
        }
        $.ajax({
            url: '/update',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ id, site_name, task, owner, contact, phone, summary, project_cost, execution_cost }),
            success: function(response) {
                alert('Task updated successfully');
            },
            error: function() {
                alert('Failed to update task');
            }
        });
    });

    // Delegate Delete button click for dynamic cards
    $('#taskCards').on('click', '.delete-btn', function() {
        const card = $(this).closest('.task-card');
        const id = card.data('id');
        if (!confirm('Are you sure you want to delete this task? This action cannot be undone.')) {
            return;
        }
        $.ajax({
            url: '/delete/' + id,
            method: 'DELETE',
            success: function(response) {
                card.remove();
            },
            error: function() {
                alert('Failed to delete task');
            }
        });
    });

    // Delegate Status button click for dynamic cards
    $('#taskCards').on('click', '.status-btn', function() {
        const btn = $(this);
        const card = btn.closest('.task-card');
        const id = card.data('id');
        const newStatus = btn.data('status');
        // Gather all other fields for update
        const site_name = card.find('[data-field="site_name"]').text().trim();
        const task = card.find('.badge').text().trim();
        const owner = card.find('[data-field="owner"]').text().trim();
        const contact = card.find('[data-field="contact"]').text().trim();
        const phone = card.find('[data-field="phone"]').text().trim();
        const summary = card.find('[data-field="summary"]').text().trim();
        const project_cost_text = card.find('[data-field="project_cost"]').text().trim();
        const execution_cost_text = card.find('[data-field="execution_cost"]').text().trim();
        const project_cost = parseInt(project_cost_text, 10);
        const execution_cost = parseInt(execution_cost_text, 10);
        if (isNaN(project_cost) || project_cost < 0 || isNaN(execution_cost) || execution_cost < 0) {
            alert('Project Cost and Execution Cost must be non-negative integers');
            return;
        }
        $.ajax({
            url: '/update',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ id, site_name, task, owner, contact, phone, summary, project_cost, execution_cost, status: newStatus }),
            success: function(response) {
                // Update indicator
                card.find('.status-indicator').attr('data-status', newStatus);
                // Optionally, highlight the active button
                card.find('.status-btn').removeClass('active');
                btn.addClass('active');
            },
            error: function() {
                alert('Failed to update status');
            }
        });
    });

    // Search functionality
    $('#searchBtn').click(function(e) {
        e.preventDefault();
        const query = $('#searchInput').val().trim();
        const type = $('#searchType').val();
        if (!query) return;
        $.ajax({
            url: '/search',
            method: 'GET',
            data: { q: query, type: type },
            success: function(tasks) {
                // Clear current cards
                $('#taskCards').empty();
                // Add filtered cards
                tasks.forEach(function(task) {
                    const cardHtml = `<div class=\"col-md-4 mb-4 task-card\" data-id=\"${task.id}\">\
                        <div class=\"card\">\
                          <div class=\"card-body\">\
                            <h6 class=\"text-primary mb-2\"><strong>Site Name:</strong> <span class=\"editable\" contenteditable=\"true\" data-field=\"site_name\">${task.site_name}</span></h6>\
                            <h5 class=\"card-title\">\
                              <span class=\"badge bg-primary\">${task.task}</span>\
                            </h5>\
                            <p class=\"card-text mb-1\"><strong>Owner:</strong> <span class=\"editable\" contenteditable=\"true\" data-field=\"owner\">${task.owner}</span></p>\
                            <p class=\"card-text mb-1\"><strong>Contact Email:</strong> <span class=\"editable\" contenteditable=\"true\" data-field=\"contact\">${task.contact}</span></p>\
                            <p class=\"card-text mb-1\"><strong>Phone:</strong> <span class=\"editable\" contenteditable=\"true\" data-field=\"phone\">${task.phone}</span></p>\
                            <p class=\"card-text mb-3 truncate-2\"><strong>Summary/Comment:</strong> <span class=\"editable\" contenteditable=\"true\" data-field=\"summary\">${task.summary}</span></p>\
                            <button class=\"btn btn-sm btn-primary save-btn\">Save</button>\
                            <button class=\"btn btn-sm btn-danger delete-btn\">Delete</button>\
                            <a href=\"/task/${task.id}\" class=\"btn btn-sm btn-info\">View</a>\
                            <div class=\"mt-auto\">\
                              <small class=\"text-muted\">Created: ${task.created_at ? task.created_at.replace('T', ' ').slice(0, 19) : ''}</small>\
                            </div>\
                          </div>\
                        </div>\
                      </div>`;
                    $('#taskCards').append(cardHtml);
                });
            },
            error: function() {
                alert('Search failed');
            }
        });
    });
    $('#clearSearchBtn').click(function(e) {
        e.preventDefault();
        location.reload();
    });
});
