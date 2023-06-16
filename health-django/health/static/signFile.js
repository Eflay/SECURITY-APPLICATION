function signFilePatient(file) {
    privateKey = forge.pki.privateKeyFromPem(atob(sessionStorage.getItem("privatekey")))

    var md = forge.md.sha256.create();
    md.update(file, 'utf8')
    signature = btoa(privateKey.sign(md))

    return signature
}

function signFileDoctor(file) {
    privateKey = forge.pki.privateKeyFromPem(atob(sessionStorage.getItem("privatekey")))

    var md = forge.md.sha256.create();
    md.update(file, 'utf8')
    signature = btoa(privateKey.sign(md))

    return signature
}


function verifySignature(signature, pubKey, file) {
    pubKey = forge.pki.publicKeyFromPem(atob(pubKey))
    var md = forge.md.sha256.create();
    md.update(file, 'utf8')
    try {
        var verified = pubKey.verify(md.digest().bytes(), atob(signature))
    } catch {
        alert("Erreur, impossible de vérifier la signature")
    }

    if (verified) {
        decryptFile();
    } else {
        alert("Docteur corrompu") // A modifier
    }

}