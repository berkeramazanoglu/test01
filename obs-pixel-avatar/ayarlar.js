// ===== AVATAR AYARLARI =====
// Bu dosyayı Not Defteri ile açıp değiştirebilirsin. Kaydettikten sonra
// OBS'te avatar kaynağına sağ tıkla → Özellikler → "Mevcut sayfanın önbelleğini yenile".
window.AVATAR_AYAR = {
  // OBS → Araçlar → WebSocket Sunucu Ayarları'ndaki şifre ("Kimlik doğrulamayı etkinleştir" açıksa)
  sifre: '',

  // OBS'teki mikrofon kaynağının adı ya da bir parçası (boş bırakırsan adında "mic/mik/aux" geçeni bulur)
  mikrofon: '',

  // Ağız eşikleri (desibel). Ağız az açılıyorsa ikisini de küçült (ör. -48 / -36),
  // klavye sesinde bile açılıyorsa büyüt (ör. -36 / -26).
  yarim: -42,
  acik: -30,

  // Piksel büyüklüğü. 6 → 360x396 piksel. OBS'teki genişlik/yüksekliği buna göre ayarla.
  olcek: 6,

  // true yaparsan avatarın altında ses seviyesi ve OBS kaynak adları görünür (ayar yaparken aç, sonra kapat)
  ayar_ekrani: false,
};
