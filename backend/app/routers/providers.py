from fastapi import APIRouter, Depends, HTTPException, status, Response
from typing import List, Optional
from datetime import datetime
import sys
import os
import io

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.core.security import get_current_user, require_role
from app.core.dashboard import (
    build_last_7_days_metrics,
    build_recent_biomarkers,
    build_weekly_patient_summary,
    build_weekly_summary,
    get_daily_goals,
)
from app.routers.notifications import create_notification_internal

# try to import reportlab for pdf generation
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("DEBUG: reportlab not available, pdf export disabled")

router = APIRouter(prefix="/providers", tags=["healthcare providers"])


def get_name_parts(user: dict):
    first_name = (user.get("first_name") or "").strip()
    last_name = (user.get("last_name") or "").strip()
    if first_name or last_name:
        return first_name, last_name

    full_name = (user.get("name") or "").strip()
    if not full_name:
        return "", ""

    parts = full_name.split()
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], " ".join(parts[1:])


@router.get("/dashboard")
async def get_provider_dashboard(current_user: dict = Depends(require_role("healthcare_provider"))):
    from app.core import firestore
    from app.core.security import public_role

    provider_id = current_user["uid"]
    provider = firestore.get_provider(provider_id) or {}
    patient_ids = firestore.get_patients_for_provider(provider_id)
    alerts = firestore.get_patient_alerts(provider_id)

    patients = []
    clients_logged_on_today = 0
    today = datetime.now().date().isoformat()
    pending_consents = []

    for patient_id in patient_ids:
        patient = firestore.get_user(patient_id) or {"uid": patient_id}
        consent = firestore.get_consent_settings(patient_id)
        can_access = firestore.can_provider_access_patient(provider_id, patient_id)
        first_name, last_name = get_name_parts(patient)
        display_name = " ".join(part for part in [first_name, last_name] if part).strip() or patient.get("email") or patient_id
        records = firestore.get_all_biomarkers(patient_id) if can_access else []
        metrics_last_7_days = build_last_7_days_metrics(records) if can_access else build_last_7_days_metrics([])
        recent_biomarkers = build_recent_biomarkers(records, limit=10) if can_access else []
        summary = build_weekly_patient_summary(records) if can_access and records else None
        weekly_summary = build_weekly_summary(records) if can_access and records else None
        patient_alerts = [
            alert for alert in alerts
            if alert.get("patient_id") == patient_id and alert.get("enabled", True)
        ]
        last_activity = recent_biomarkers[-1]["timestamp"] if recent_biomarkers else None
        consent_granted = bool(consent.get("share_with_healthcare_providers", False))

        if can_access and any(
            day["date"] == today and day["value"] != "N/A"
            for metric_days in metrics_last_7_days.values()
            for day in metric_days
        ):
            clients_logged_on_today += 1

        if not consent_granted:
            pending_consents.append({
                "uid": patient_id,
                "email": patient.get("email", ""),
                "requested_at": patient.get("updated_at") or patient.get("created_at"),
                "status": "pending",
            })

        patients.append({
            "uid": patient_id,
            "id": patient_id,
            "name": display_name,
            "fname": first_name,
            "lname": last_name,
            "email": patient.get("email", ""),
            "age": patient.get("age"),
            "gender": patient.get("gender"),
            "consent_granted": consent_granted,
            "consent_updated_at": patient.get("updated_at"),
            "last_activity": last_activity,
            "status": "ACTIVE" if consent_granted else "INACTIVE",
            "alerts": len(patient_alerts),
            "recent_biomarkers": recent_biomarkers,
            "summary": summary,
            "weekly_summary": weekly_summary,
            "daily_goals": get_daily_goals(patient),
            "metrics_last_7_days": metrics_last_7_days,
        })

    total_clients = len(patients)
    provider_name = provider.get("name") or " ".join(part for part in get_name_parts(provider) if part).strip() or current_user.get("email") or "Doctor"
    provider_profile = {
        "uid": provider_id,
        "email": provider.get("email") or current_user.get("email"),
        "name": provider_name,
        "specialty": provider.get("specialty"),
        "role": public_role(provider.get("role") or current_user.get("role")),
        "created_at": provider.get("created_at"),
        "updated_at": provider.get("updated_at"),
    }

    return {
        "provider_id": provider_id,
        "provider_email": provider_profile["email"],
        "provider_name": provider_name,
        "provider_profile": provider_profile,
        "patients": patients,
        "pending_consents": pending_consents,
        "total_clients": total_clients,
        "active_alerts_sent": len([alert for alert in alerts if alert.get("enabled", True)]),
        "clients_logged_on_today": min(clients_logged_on_today, total_clients),
        "clients": patients,
    }


@router.get("/patients")
async def get_patients(current_user: dict = Depends(require_role("healthcare_provider"))):
    from app.core import firestore

    try:
        provider_id = current_user["uid"]
        patient_ids = firestore.get_patients_for_provider(provider_id)

        patients = []
        for pid in patient_ids:
            if not firestore.can_provider_access_patient(provider_id, pid):
                continue
            patient = firestore.get_user(pid) or {"uid": pid}
            patients.append({
                "uid": pid,
                "email": patient.get("email"),
                "age": patient.get("age"),
                "gender": patient.get("gender")
            })

        return {
            "provider_id": provider_id,
            "patients": patients,
            "count": len(patients)
        }
    except Exception as e:
        print(f"DEBUG: get patients error: {e}")
        raise HTTPException(status_code=500, detail="failed to fetch patients")


@router.get("/patients/{patient_id}/data")
async def get_patient_data(
    patient_id: str,
    current_user: dict = Depends(require_role("healthcare_provider"))
):
    from app.core import firestore

    if not current_user.get("mfa_verified", False):
        raise HTTPException(status_code=403, detail="MFA verification required")

    patient = firestore.get_user(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="patient not found")

    if not firestore.can_provider_access_patient(current_user["uid"], patient_id):
        raise HTTPException(status_code=403, detail="provider does not have access to this patient")

    firestore.create_audit_log(
        user_id=current_user["uid"],
        target_user_id=patient_id,
        action="view_patient_data",
        category="data_access",
        status="success",
    )

    recent_biomarkers = firestore.get_recent_biomarkers(patient_id, limit=10)
    all_biomarkers = firestore.get_all_biomarkers(patient_id)
    devices = firestore.get_user_devices(patient_id)
    manual_entries = firestore.get_manual_entries(patient_id)
    consent = firestore.get_consent_settings(patient_id)

    total_steps = sum(r.get("steps", 0) or 0 for r in all_biomarkers)
    total_calories = sum(r.get("calories", 0) or 0 for r in all_biomarkers)
    heart_rates = [r.get("heart_rate") for r in all_biomarkers if r.get("heart_rate")]
    avg_heart_rate = sum(heart_rates) // len(heart_rates) if heart_rates else 0

    provider_alerts = [
        alert for alert in firestore.get_patient_alerts(current_user["uid"])
        if alert.get("patient_id") == patient_id
    ]

    return {
        "provider_id": current_user["uid"],
        "patient": {
            "uid": patient.get("uid", patient_id),
            "email": patient.get("email"),
            "age": patient.get("age"),
            "gender": patient.get("gender"),
            "language": patient.get("language"),
        },
        "consent": {
            "share_with_healthcare_providers": consent.get("share_with_healthcare_providers", False)
        },
        "summary": {
            "records_found": len(all_biomarkers),
            "total_steps": total_steps,
            "total_calories": total_calories,
            "avg_heart_rate": avg_heart_rate,
            "devices_connected": len(devices),
            "manual_entries": len(manual_entries),
        },
        "recent_biomarkers": recent_biomarkers,
        "devices": devices,
        "manual_entries": manual_entries,
        "provider_alerts": provider_alerts,
    }


@router.post("/alerts")
async def set_patient_alert(
    patient_id: str,
    alert_config: dict,
    current_user: dict = Depends(require_role("healthcare_provider"))
):
    from app.core import firestore
    try:
        provider_id = current_user["uid"]

        if not current_user.get("mfa_verified", False):
            raise HTTPException(status_code=403, detail="MFA verification required")

        patient = firestore.get_user(patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="patient not found")

        if not firestore.can_provider_access_patient(provider_id, patient_id):
            raise HTTPException(status_code=403, detail="provider does not have access to this patient")

        # basic validation
        required = ["biomarker_type", "condition", "threshold"]
        for field in required:
            if field not in alert_config:
                raise HTTPException(status_code=400, detail=f"missing {field}")

        valid_conditions = ["greater_than", "less_than", "equals"]
        if alert_config.get("condition") not in valid_conditions:
            raise HTTPException(status_code=400, detail="invalid condition")

        alert = {
            "patient_id": patient_id,
            "biomarker_type": alert_config["biomarker_type"],
            "condition": alert_config["condition"],
            "threshold": alert_config["threshold"],
            "message": alert_config.get("message", ""),
            "enabled": alert_config.get("enabled", True)
        }

        alert_id = firestore.add_patient_alert(provider_id, alert)
        if not alert_id:
            raise HTTPException(status_code=500, detail="failed to save alert")

        message = alert_config.get("message", "")
        if not message:
            message = f"Your provider set an alert for {alert_config['biomarker_type']}"

        create_notification_internal(
            user_id=patient_id,
            title="Provider Alert",
            message=message,
            notification_type="provider_alert",
            data={
                "alert_id": alert_id,
                "provider_id": provider_id,
                "biomarker_type": alert_config["biomarker_type"],
                "condition": alert_config["condition"],
                "threshold": alert_config["threshold"],
            }
        )

        firestore.create_audit_log(
            user_id=provider_id,
            target_user_id=patient_id,
            action="set_provider_alert",
            category="sharing",
            status="success",
            details={"alert_id": alert_id},
        )

        return {
            "provider_id": provider_id,
            "patient_id": patient_id,
            "alert_id": alert_id,
            "message": "patient alert saved"
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG: set patient alert error: {e}")
        raise HTTPException(status_code=500, detail="failed to set patient alert")


@router.get("/alerts")
async def list_patient_alerts(current_user: dict = Depends(require_role("healthcare_provider"))):
    from app.core import firestore
    try:
        provider_id = current_user["uid"]
        alerts = firestore.get_patient_alerts(provider_id)
        return {
            "provider_id": provider_id,
            "alerts": alerts,
            "count": len(alerts)
        }
    except Exception as e:
        print(f"DEBUG: list patient alerts error: {e}")
        raise HTTPException(status_code=500, detail="failed to fetch alerts")


@router.get("/patients/{patient_id}/export")
async def export_patient_pdf(
    patient_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: dict = Depends(require_role("healthcare_provider"))
):
    """
    export patient biomarker data as pdf report.
    healthcare providers can download patient data for their records.
    """
    from app.core import firestore

    if not REPORTLAB_AVAILABLE:
        raise HTTPException(status_code=501, detail="pdf generation not available")

    try:
        provider_id = current_user["uid"]

        if not current_user.get("mfa_verified", False):
            raise HTTPException(status_code=403, detail="MFA verification required")

        # get patient data
        patient = firestore.get_user(patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="patient not found")

        if not firestore.can_provider_access_patient(provider_id, patient_id):
            raise HTTPException(status_code=403, detail="provider does not have access to this patient")

        firestore.create_audit_log(
            user_id=provider_id,
            target_user_id=patient_id,
            action="export_patient_pdf",
            category="data_access",
            status="success",
        )

        # get patient's biomarker data
        biomarkers = firestore.get_all_biomarkers(patient_id)

        # filter by date range if provided
        if start_date or end_date:
            filtered = []
            for record in biomarkers:
                ts = record.get("timestamp", "")
                if ts:
                    try:
                        record_date = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                        date_str = record_date.strftime("%Y-%m-%d")

                        if start_date and date_str < start_date:
                            continue
                        if end_date and date_str > end_date:
                            continue
                        filtered.append(record)
                    except:
                        pass
            biomarkers = filtered

        print(f"DEBUG: generating pdf for patient {patient_id}, {len(biomarkers)} records")

        # create pdf in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []

        # styles
        styles = getSampleStyleSheet()
        title_style = styles['Heading1']
        heading_style = styles['Heading2']
        normal_style = styles['Normal']

        # title
        elements.append(Paragraph("PulseLink Patient Report", title_style))
        elements.append(Spacer(1, 20))

        # patient info
        elements.append(Paragraph("Patient Information", heading_style))
        patient_email = patient.get("email", "N/A")
        patient_role = patient.get("role", "user")
        elements.append(Paragraph(f"Email: {patient_email}", normal_style))
        elements.append(Paragraph(f"Patient ID: {patient_id}", normal_style))
        elements.append(Spacer(1, 20))

        # report metadata
        elements.append(Paragraph("Report Details", heading_style))
        elements.append(Paragraph(f"Generated by: {provider_id}", normal_style))
        elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", normal_style))
        if start_date:
            elements.append(Paragraph(f"Date Range: {start_date} to {end_date or 'now'}", normal_style))
        elements.append(Paragraph(f"Total Records: {len(biomarkers)}", normal_style))
        elements.append(Spacer(1, 20))

        # summary stats
        if biomarkers:
            elements.append(Paragraph("Summary Statistics", heading_style))

            total_steps = sum(r.get("steps", 0) or 0 for r in biomarkers)
            total_calories = sum(r.get("calories", 0) or 0 for r in biomarkers)
            heart_rates = [r.get("heart_rate") for r in biomarkers if r.get("heart_rate")]
            avg_hr = sum(heart_rates) // len(heart_rates) if heart_rates else 0

            summary_data = [
                ["Metric", "Total/Average"],
                ["Records", str(len(biomarkers))],
                ["Total Steps", f"{total_steps:,}"],
                ["Total Calories", f"{total_calories:.1f}"],
                ["Avg Heart Rate", f"{avg_hr} BPM"],
            ]

            summary_table = Table(summary_data)
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(summary_table)
            elements.append(Spacer(1, 20))

            # detailed data table
            elements.append(Paragraph("Detailed Records", heading_style))

            table_data = [["Timestamp", "Heart Rate", "Steps", "Calories", "Device"]]
            for record in biomarkers[:50]:  # limit to 50 records
                table_data.append([
                    record.get("timestamp", "")[:16],
                    str(record.get("heart_rate", "-")),
                    str(record.get("steps", "-")),
                    str(record.get("calories", "-")),
                    record.get("device_id", "-")[:15]
                ])

            data_table = Table(table_data)
            data_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
            ]))
            elements.append(data_table)
        else:
            elements.append(Paragraph("No biomarker data available for this patient.", normal_style))

        # footer
        elements.append(Spacer(1, 30))
        elements.append(Paragraph("--- End of Report ---", normal_style))
        elements.append(Paragraph("Generated by PulseLink Healthcare System", styles['Italic']))

        # build pdf
        doc.build(elements)

        # get pdf content
        pdf_content = buffer.getvalue()
        buffer.close()

        # filename
        filename = f"patient_{patient_id}_{datetime.now().strftime('%Y%m%d')}.pdf"

        print(f"DEBUG: pdf generated, size: {len(pdf_content)} bytes")

        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG: pdf export error: {e}")
        raise HTTPException(status_code=500, detail=f"pdf generation failed: {e}")
