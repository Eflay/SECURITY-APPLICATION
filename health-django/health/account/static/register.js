let formElt = document.getElementById("registerForm")

formElt.addEventListener("submit", async (e) => {
    e.preventDefault()

    // Get Form field
    let emailElt = formElt.elements["id_email"]
    let passwordElt = formElt.elements["id_password1"]
    let passwordConfirmElt = formElt.elements["id_password2"]
    let protectedSymetricKeyElt = formElt.elements["id_protected_symetric_key"]
    let protectedPrivateKeyElt = formElt.elements["id_protected_private_key"]
    let publicKeyElt = formElt.elements["id_public_key"]
    // Check if password field is not empty and password match to password confirm before generate cyptographic material
    if(passwordElt.value !== "" && passwordConfirmElt.value !== "") {
        if(passwordElt.value === passwordConfirmElt.value) {
            let regexPassword = new RegExp('(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[^A-Za-z0-9])(?=.{8,})')

            if(regexPassword.test(passwordElt.value)) {
                // Generate cryptographic material
                let [
                    b64MasterPasswordHash, 
                    resultProtectedSymetricKey, 
                    resultProtectedPrivateKey, 
                    b64PublicKey
                ] = await generateCrypto(emailElt.value.toLowerCase(), passwordElt.value)

                // Replace DOM form by cryptographic material
                passwordElt.value = b64MasterPasswordHash
                passwordConfirmElt.value = b64MasterPasswordHash
                protectedSymetricKeyElt.value = resultProtectedSymetricKey
                protectedPrivateKeyElt.value = resultProtectedPrivateKey
                publicKeyElt.value = b64PublicKey
            
                formElt.submit()
            } else {
                passwordElt.value = ""
                passwordConfirmElt.value = ""

                Swal.fire({
                    icon: 'info',
                    text: "The password must have at least 8 characters, one upper case letter, one lower case letter, one number and one special character.",
                    confirmButtonColor: '#3498db'
                })
            }
        } else {
            passwordElt.value = ""
            passwordConfirmElt.value = ""

            Swal.fire({
                icon: 'info',
                text: "Password confirmation is incorrect.",
                confirmButtonColor: '#3498db'
            })
        }
    }
})

async function generateCrypto(email, password) {
    // Generate b64 RSA keypair
    let b64PrivateKey = ''
    let b64PublicKey = ''
    await GenerateRSA()
        .then((keypair) => {
            b64PrivateKey = keypair.b64PrivateKey
            b64PublicKey = keypair.b64PublicKey
        })
        .catch((err) => {
            console.error('Error while generating the RSA key pair:', err);
        });
    
    // Generate Master Key with password and email by PBKDF2-SHA256
    let MasterKey = await PBKDF2SHA256(password, email, 600000, 32)

    // Generate Master Password Hash with Master Key and password by PBKDF2-SHA256
    let masterPasswordHash = await PBKDF2SHA256(MasterKey, password, 1, 64)
    let b64MasterPasswordHash = arrayBufferToB64(masterPasswordHash)

    // Generate Protected Symetric Key with Master Key by AES256-GCM
    let SymetricKey = forge.random.getBytesSync(32);
    let MasterKey_Buffer = forge.util.createBuffer(MasterKey, 'raw');
    let protectedSymetricKey = encryptMessage(MasterKey_Buffer, SymetricKey)

    // Generate Protected Private Key with Symetric Key by AES-256-GCM
    const textEncoder = new TextEncoder("utf-8");
    let private_key = textEncoder.encode(b64PrivateKey)
    protectedPrivateKey = encryptMessage(SymetricKey, private_key)

    return [b64MasterPasswordHash, protectedSymetricKey, protectedPrivateKey, b64PublicKey]
}
