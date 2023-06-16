function encryptSymetricKey(public_key) {
  var key = sessionStorage.getItem("symkey");

  let pubKey = forge.pki.publicKeyFromPem(atob(public_key));
  const encryptText = btoa(pubKey.encrypt(forge.util.encodeUtf8(key)));

  let formElt = document.getElementById("sign-form")

  formElt.addEventListener("submit", (e) => {
    e.preventDefault()
    var proSymKey = document.getElementById("id_protected_symetric_key");

    proSymKey.value = encryptText

    formElt.submit()
  })
}
