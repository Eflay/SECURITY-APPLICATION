function fingerprint(public_key) {
    let pubKey = forge.pki.publicKeyFromPem(atob(public_key));

    const pubKeyFingerprint = forge.pki.getPublicKeyFingerprint(pubKey, {
        md : forge.md.sha256.create(),
        encoding : 'hex',
        delimiter : ':'
    });

    document.getElementById("id_fingerprint").textContent = pubKeyFingerprint;
}