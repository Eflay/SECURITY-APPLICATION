function encryptFolder(role) {
    let formElt = document.getElementById("sign-form")

    formElt.addEventListener("submit", (e) => {
        e.preventDefault()
        var content = document.getElementById("id_content");
        var name_folder = document.getElementById("id_name");
        var encryptedFolderContent = null;
        var encryptedFolderName = null;
    
        symkey = sessionStorage.getItem("symkey");

        if (role == 'DOCTOR') {
            privateKey = atob(sessionStorage.getItem("privatekey"));
            let privKey = forge.pki.privateKeyFromPem(privateKey);
            decryptSymKey = privKey.decrypt(atob(accord.value));
            symkey = decryptSymKey;
        }
    
        symkey_buffer = forge.util.createBuffer(forge.util.hexToBytes(symkey), "raw");
    
        test = forge.util.createBuffer(forge.util.hexToBytes(symkey), "raw");
    
        encryptedFolderContent = encryptMessage(symkey_buffer, content.value);
        encryptedFolderName = encryptMessage(test, name_folder.value);
    
        content.value = btoa(encryptedFolderContent);

        console.log(content.value);

        name_folder.value = btoa(encryptedFolderName);

        if (role == 'DOCTOR'){
            formElt.elements["id_doctor_sign"].value = signFileDoctor(content.value)
            formElt.elements["id_patient_sign"].value = null
        } else {
            formElt.elements["id_patient_sign"].value = signFilePatient(content.value)
            formElt.elements["id_doctor_sign"].value = null

        }

        formElt.submit()
    })
}