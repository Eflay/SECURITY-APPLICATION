sessionStorage.clear()

let formElt = document.getElementById("loginForm")

formElt.addEventListener('submit', async (e) => {
    e.preventDefault();

    // Get Form field
    let emailElt = formElt.elements["id_email"]
    let passwordElt = formElt.elements["id_password"]

    // Check if mail and password field is not empty before generate cyptographic material
    if (emailElt.value !== "" & passwordElt.value !== "") {
        // Store data to sessionStorage
        sessionStorage.setItem("mail", btoa(emailElt.value.toLowerCase()))
        sessionStorage.setItem("password", btoa(passwordElt.value))

        // Generate cryptographic material
        let b64MasterPasswordHash = await generateCrypto(emailElt.value.toLowerCase(), passwordElt.value)

        // Replace DOM form by cryptographic material
        passwordElt.value = b64MasterPasswordHash
    }

    formElt.submit()
})


async function generateCrypto(email, password) {
    // Generate Master Key
    let MasterKey = await PBKDF2SHA256(password, email, 600000, 32)

    // Generate Master Password hash
    let MasterPasswordHash = await PBKDF2SHA256(MasterKey, password, 1, 64)
    let b64MasterPasswordHash = arrayBufferToB64(MasterPasswordHash)

    return b64MasterPasswordHash;
}