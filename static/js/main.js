document.getElementById('bookingForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const statusDiv = document.getElementById('bookingStatus');
    statusDiv.style.display = 'none';
    
    const formData = {
        firstName: document.getElementById('firstName').value,
        lastName: document.getElementById('lastName').value,
        dob: document.getElementById('dob').value
    };
    
    try {
        const response = await fetch('/book', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        statusDiv.className = `alert ${result.status === 'success' ? 'alert-success' : 'alert-danger'}`;
        statusDiv.textContent = result.message;
        statusDiv.style.display = 'block';
        
        if (result.status === 'success') {
            document.getElementById('bookingForm').reset();
        }
    } catch (error) {
        statusDiv.className = 'alert alert-danger';
        statusDiv.textContent = 'An error occurred while booking the flight.';
        statusDiv.style.display = 'block';
    }
});