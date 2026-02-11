// Backend server URL
// Change this to your deployed URL later
const API_URL = 'http://127.0.0.1:5000';

// Store the summary PDF
let summaryBlob = null;

// Main function - called when user clicks "Summarize PDF"
async function uploadPDF() {

    // Get the file input element
    const fileInput = document.getElementById('pdfFile');
    const file = fileInput.files[0];

    // Validate: check if file was selected
    if (!file) {
        showStatus('Please select a PDF file first!', 'error');
        return;
    }

    // Validate: check if it's actually a PDF
    if (!file.name.endsWith('.pdf')) {
        showStatus('Please select a PDF file (.pdf)', 'error');
        return;
    }

    // Get button and disable it during upload
    const uploadBtn = document.getElementById('uploadBtn');
    uploadBtn.disabled = true;
    uploadBtn.textContent = 'Processing...';

    // Hide previous results
    document.getElementById('result').classList.add('hidden');

    // Show loading status
    showStatus(
        'Uploading PDF and generating summary... This may take 10-30 seconds.',
        'loading'
    );

    try {

        // Create FormData to send file
        const formData = new FormData();
        formData.append('file', file);

        // Send request to Flask backend
        const response = await fetch(`${API_URL}/summarize`, {
            method: 'POST',
            body: formData
        });

        // Check if request was successful
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to summarize PDF');
        }

        // Get the PDF blob from response
        summaryBlob = await response.blob();

        // Show success message
        showStatus('✅ Summary generated successfully!', 'success');

        // Show download button
        document.getElementById('result').classList.remove('hidden');

        // Attach download function to button
        document.getElementById('downloadBtn').onclick = downloadSummary;

    } catch (error) {

        // Show error message
        showStatus(`❌ Error: ${error.message}`, 'error');
        console.error('Upload error:', error);

    } finally {

        // Re-enable button
        uploadBtn.disabled = false;
        uploadBtn.textContent = 'Summarize PDF';
    }
}

// Function to download the summary PDF
function downloadSummary() {

    if (!summaryBlob) {
        showStatus('No summary available to download', 'error');
        return;
    }

    // Create a download link
    const url = window.URL.createObjectURL(summaryBlob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'summary.pdf';

    // Trigger download
    document.body.appendChild(a);
    a.click();

    // Cleanup
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);

    showStatus('📥 Summary downloaded!', 'success');
}

// Helper function to show status messages
function showStatus(message, type) {

    const statusDiv = document.getElementById('status');
    statusDiv.textContent = message;

    // Remove all status classes
    statusDiv.className = 'status';

    // Add the appropriate class
    if (type) {
        statusDiv.classList.add(type);
    }
}
