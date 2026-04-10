export default function DataPrivacySection() {
  return (
    <section id="data-privacy" className="scroll-mt-8">
      <h2 className="mb-3 text-lg font-bold" style={{ color: "#1a1a1a" }}>
        Data and Privacy
      </h2>
      <p className="mb-4 text-sm leading-relaxed" style={{ color: "#6b7280" }}>
        We securely store your data on Google's Firestorestore and process in
        order to offer you the basic PulseLink service, such as your health metrics,
        wearable device data, and shared information between you and your healthcare
        providers. By using PulseLink, you allow us to provide this essential functionality
        and enable real-time health tracking.
      </p>
      <p className="text-sm leading-relaxed" style={{ color: "#6b7280" }}>
        {"You can stop this by "}
        <a href="/auth/delete-account" className="font-semibold underline" style={{ color: "#ef5350" }}>
          deleting your account
        </a>
        {" and "}
        <a href="#" className="font-semibold underline" style={{ color: "#1e88e5" }}>
          unsyncing your linked devices below.
        </a>
      </p>
    </section>
  )
}