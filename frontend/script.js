const API ="https://data-quality-backend-1.onrender.com";

let totalFiles = 0;
let lastResult = null;
let currentUser = "";

// TOAST
function showToast(msg, type="success") {
    const t = document.getElementById("toast");
    t.innerText = msg;
    t.className = type + " show";
    setTimeout(() => t.className = "", 3000);
}

// LOADER
function showLoader(){ document.getElementById("loader").style.display="flex"; }
function hideLoader(){ document.getElementById("loader").style.display="none"; }

// AUTH
// ================= LOGIN SYSTEM =================

// SWITCH PAGES
function showRegister() {
    document.getElementById("login-box").style.display = "none";
    document.getElementById("register-box").style.display = "block";
}

function showLogin() {
    document.getElementById("register-box").style.display = "none";
    document.getElementById("login-box").style.display = "block";
}

// LOGIN
function login() {
    const username = document.getElementById("login-username").value;
    const password = document.getElementById("login-password").value;

    fetch(API + "/login", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({username, password})
    })
    .then(res => {
        if (!res.ok) throw new Error();
        return res.json();
    })
    .then(() => {
        currentUser = username;
        showToast("Login successful ");
        openDashboard();
    })
    .catch(() => {
        showToast("Invalid credentials ", "error");
    });
}

// REGISTER
function register() {
    const username = document.getElementById("register-username").value;
    const password = document.getElementById("register-password").value;
    const confirm = document.getElementById("confirm-password").value;

    if (password !== confirm) {
        showToast("Passwords do not match ", "error");
        return;
    }

    fetch(API + "/register", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({username, password})
    })
    .then(res => res.json())
    .then(data => {
        if (data.message.includes("exists")) {
            showToast("User already exists ", "error");
        } else {
            showToast("Account created ");
            showLogin();
        }
    });
}

// DASHBOARD
function openDashboard(){
    document.getElementById("auth-box").style.display="none";
    document.getElementById("main").style.display="flex";
    document.getElementById("welcome").innerText = "Welcome, " + currentUser;
}

// LOGOUT
function logout(){
    location.reload();
}

// UPLOAD
function upload(){
    const file = document.getElementById("file").files[0];
    if(!file){
        showToast("Select file","error");
        return;
    }

    showLoader();

    const formData = new FormData();
    formData.append("file",file);

    fetch(API + "/upload",{method:"POST",body:formData})
    .then(res=>res.json())
    .then(data=>{
        lastResult = data;

        totalFiles++;
        document.getElementById("files").innerText = totalFiles;
        document.getElementById("errors").innerText = data.errors;
        document.getElementById("quality").innerText = data.quality + "%";

        document.getElementById("summary").innerHTML =
            `Rows: ${data.rows}<br>Cols: ${data.cols}`;

        const list = document.getElementById("error-list");
        list.innerHTML="";
        data.error_list.forEach(e=>{
            const div = document.createElement("div");
            div.className="error-item";
            div.innerText=e;
            list.appendChild(div);
        });

        showToast("Analysis done");
    })
    .finally(()=>hideLoader());
}

// DOWNLOAD
function downloadReport(){
    if (!lastResult) {
        showToast("Please analyze file first", "error");
        return;
    }

    showLoader();

    fetch(API + "/report", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(lastResult)
    })
    .then(response => {
        if (!response.ok) throw new Error("Network error");
        return response.blob();   // ✅ FIX
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob);

        const a = document.createElement("a");
        a.href = url;
        a.download = "report.pdf";
        document.body.appendChild(a);
        a.click();
        a.remove();

        window.URL.revokeObjectURL(url);

        showToast("Downloaded successfully");
    })
    .catch(() => {
        showToast("Download failed", "error");
    })
    .finally(() => hideLoader());
}