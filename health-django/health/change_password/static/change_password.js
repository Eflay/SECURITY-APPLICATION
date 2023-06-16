let SymetricKey
let private_key
let b64PublicKey

let formElt = document.getElementById("registerForm")
let passwordElt = formElt.elements["id_old_password"]
let passwordElt1 = formElt.elements["id_new_password1"]
let passwordConfirmElt = formElt.elements["id_new_password2"]
let protectedSymetricKeyElt = formElt.elements["id_protected_symetric_key"]
let protectedPrivateKeyElt = formElt.elements["id_protected_private_key"]
let publicKeyElt = formElt.elements["id_public_key"]
let roleUser = formElt.elements["role"].value


formElt.addEventListener('submit', async (e) => {
    e.preventDefault()

    // Get Form field
    let emailElt = formElt.elements["id_email"]

    // Check if password field is not empty and password match to password confirm before generate cyptographic material
    if (emailElt.value !== "" & passwordElt.value !== "" & passwordElt1.value !== "" && passwordConfirmElt.value !== "") {

        // Generate cryptographic material
        let b64MasterPasswordHash = await generateCryptoAuthenticate(emailElt.value, passwordElt.value)

        // Replace DOM form by cryptographic material
        passwordElt.value = b64MasterPasswordHash

        if (passwordElt1.value === passwordConfirmElt.value) {
            let regexPassword = new RegExp('(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[^A-Za-z0-9])(?=.{8,})')

            if (regexPassword.test(passwordElt1.value)) {
                // Generate cryptographic material
                let [
                    b64MasterPasswordHash,
                    resultProtectedSymetricKey,
                    resultProtectedPrivateKey,
                    b64PublicKey
                ] = await generateCrypto(emailElt.value, passwordElt1.value)

                // Replace DOM form by cryptographic material
                passwordElt1.value = b64MasterPasswordHash
                passwordConfirmElt.value = b64MasterPasswordHash
                protectedSymetricKeyElt.value = resultProtectedSymetricKey
                protectedPrivateKeyElt.value = resultProtectedPrivateKey
                publicKeyElt.value = b64PublicKey

                try {
                    var files = document.getElementById("files").value;
                } catch (error) {
                    var files = false;
                }

                if (files) {
                    var data_json = JSON.parse(files);
                    for (i in data_json) {
                        data_json[i]["name"] = encrypt(data_json[i]["name"]);
                        data_json[i]["content"] = encrypt(data_json[i]["content"]);
                    };
                    data = JSON.stringify(data_json);
                    document.getElementById("files").value = data;
                };

                try {
                    var accords = document.getElementById('accords').value;
                } catch (error) {
                    var accords = false;
                }

                if (accords) {
                    var accord_json = JSON.parse(accords);
                    for (i in accord_json) {
                        if (roleUser == 'DOCTOR') {
                            var doctor_pub_key = b64PublicKey;
                            var keySymetricPatient = accord_json[i]["protected_symetric_key"];
                        } else {
                            var doctor_pub_key = accord_json[i]["public_key"];
                            SymetricKey = forge.util.bytesToHex(SymetricKey)
                            var keySymetricPatient = forge.util.encodeUtf8(SymetricKey);
                        }
                        accord_json[i]["protected_symetric_key"] = encryptSymetricKey(doctor_pub_key, keySymetricPatient);
                    };
                    accords = JSON.stringify(accord_json);
                    document.getElementById("accords").value = accords;
                };

                formElt.submit()

            } else {
                alert("The password must have at least 8 characters, one upper case letter, one lower case letter, one number and one special character.")
                window.location.reload();
            }

        } else {
            alert("Password confirmation is incorrect.")
            window.location.reload();
        }
    }



})


async function generateCryptoAuthenticate(email, password) {
    // Generate Master Key
    let MasterKey = await PBKDF2SHA256(password, email, 600000, 32)

    // Generate Master Password hash
    let MasterPasswordHash = await PBKDF2SHA256(MasterKey, password, 1, 64)
    let b64MasterPasswordHash = arrayBufferToB64(MasterPasswordHash)
    return b64MasterPasswordHash;
}

async function generateCrypto(email, password) {
    // Generate b64 RSA keypair
    let b64PrivateKey = ''
    b64PublicKey = ''
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
    SymetricKey = forge.random.getBytesSync(32);
    let MasterKey_Buffer = forge.util.createBuffer(MasterKey, 'raw');
    let protectedSymetricKey = encryptMessage(MasterKey_Buffer, SymetricKey)

    // Generate Protected Private Key with Symetric Key by AES-256-GCM
    const textEncoder = new TextEncoder("utf-8");
    private_key = textEncoder.encode(b64PrivateKey)
    protectedPrivateKey = encryptMessage(SymetricKey, private_key)
    return [b64MasterPasswordHash, protectedSymetricKey, protectedPrivateKey, b64PublicKey]
}

function encrypt(elem) {
    var encrypted = null;

    symkey_buffer = forge.util.createBuffer(SymetricKey, "raw");
    encrypted = encryptMessage(symkey_buffer, elem);
    elem = btoa(encrypted);

    return elem;
}

function encryptSymetricKey(public_key, symetricKey) {
    var key = symetricKey;
    let pubKey = forge.pki.publicKeyFromPem(atob(public_key));
    const encryptText = btoa(pubKey.encrypt(forge.util.encodeUtf8(key)));
    return encryptText;
}
