// Function to refresh the access token
async function refreshToken() {
  try {
    const response = await fetch("/api/auth/refresh", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include", // Important for sending cookies
    });

    if (!response.ok) {
      throw new Error("Token refresh failed");
    }

    return true;
  } catch (error) {
    console.error("Error refreshing token:", error);
    window.location.href = "/login";
    return false;
  }
}

// Function to handle 401 responses
async function handle401Response(response, retryRequest) {
  if (response.status === 401) {
    // Try to refresh the token
    const refreshSuccessful = await refreshToken();
    if (refreshSuccessful) {
      // Retry the original request
      return await retryRequest();
    }
  }
  return response;
}

// Intercept all fetch requests to handle 401s
const originalFetch = window.fetch;
window.fetch = async function (...args) {
  const request = args[0];
  const config = args[1];

  // Create a function to retry the original request
  const retryRequest = () => originalFetch(request, config);

  // Make the initial request
  const response = await originalFetch(...args);

  // Handle 401 responses
  return await handle401Response(response, retryRequest);
};

// Also intercept HTMX requests
document.addEventListener("htmx:beforeRequest", function (event) {
  const originalHandler = event.detail.xhr.onload;
  event.detail.xhr.onload = async function () {
    const response = this;
    if (response.status === 401) {
      // Try to refresh the token
      const refreshSuccessful = await refreshToken();
      if (refreshSuccessful) {
        // Retry the original HTMX request
        event.detail.issueRequest();
        return;
      }
    }
    if (originalHandler) {
      originalHandler.apply(this, arguments);
    }
  };
});
