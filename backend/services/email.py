"""
Email service for sending transactional emails.
Supports SMTP-based email with async background tasks.
"""

import os
import logging
import asyncio
from typing import Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from datetime import datetime

logger = logging.getLogger(__name__)


class EmailConfig:
    """Email configuration from environment variables."""

    SMTP_HOST = os.getenv("SMTP_HOST", "localhost")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "noreply@lexikon.local")
    SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "Lexikon")
    SMTP_TLS = os.getenv("SMTP_TLS", "true").lower() == "true"

    # For development/testing without real SMTP
    MOCK_EMAIL = os.getenv("MOCK_EMAIL", "false").lower() == "true"


class EmailService:
    """Email service for sending transactional emails."""

    @staticmethod
    def _get_smtp_connection():
        """Get SMTP connection."""
        if EmailConfig.MOCK_EMAIL:
            return None

        try:
            if EmailConfig.SMTP_TLS:
                server = smtplib.SMTP(EmailConfig.SMTP_HOST, EmailConfig.SMTP_PORT)
                server.starttls()
            else:
                server = smtplib.SMTP(EmailConfig.SMTP_HOST, EmailConfig.SMTP_PORT)

            if EmailConfig.SMTP_USER and EmailConfig.SMTP_PASSWORD:
                server.login(EmailConfig.SMTP_USER, EmailConfig.SMTP_PASSWORD)

            return server
        except Exception as e:
            logger.error(f"SMTP connection failed: {e}")
            raise

    @staticmethod
    def _send_email(to_email: str, subject: str, html_content: str, text_content: Optional[str] = None) -> bool:
        """
        Send email via SMTP.

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email content
            text_content: Plain text alternative (optional)

        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            # Mock email for development
            if EmailConfig.MOCK_EMAIL:
                logger.info(f"[MOCK EMAIL] To: {to_email} | Subject: {subject}")
                return True

            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{EmailConfig.SMTP_FROM_NAME} <{EmailConfig.SMTP_FROM_EMAIL}>"
            msg["To"] = to_email
            msg["Date"] = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")

            # Attach plain text version if provided
            if text_content:
                msg.attach(MIMEText(text_content, "plain"))

            # Attach HTML version (preferred)
            msg.attach(MIMEText(html_content, "html"))

            # Send email
            server = EmailService._get_smtp_connection()
            if server:
                server.send_message(msg)
                server.quit()
                logger.info(f"Email sent to {to_email}: {subject}")

            return True

        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {e}")
            return False

    @staticmethod
    def send_welcome_email(email: str, first_name: str) -> bool:
        """Send welcome email to new user."""
        subject = "Bienvenue sur Lexikon"

        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h1 style="color: #2563eb;">Bienvenue sur Lexikon!</h1>

                    <p>Bonjour {first_name},</p>

                    <p>Merci de vous être inscrit sur <strong>Lexikon</strong>, la plateforme pour construire et gérer vos ontologies.</p>

                    <h2 style="color: #1f2937;">Prochaines étapes</h2>
                    <ul>
                        <li>Complétez votre profil</li>
                        <li>Créez votre premier terme</li>
                        <li>Explorez les fonctionnalités de relations</li>
                    </ul>

                    <p>
                        <a href="https://lexikon.chessplorer.com/profile"
                           style="background-color: #2563eb; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px;">
                            Accéder à mon profil
                        </a>
                    </p>

                    <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;">

                    <p style="font-size: 12px; color: #666;">
                        L'équipe Lexikon<br>
                        <a href="https://lexikon.chessplorer.com">lexikon.chessplorer.com</a>
                    </p>
                </div>
            </body>
        </html>
        """

        text_content = f"""
        Bienvenue sur Lexikon!

        Bonjour {first_name},

        Merci de vous être inscrit sur Lexikon, la plateforme pour construire et gérer vos ontologies.

        Prochaines étapes:
        - Complétez votre profil
        - Créez votre premier terme
        - Explorez les fonctionnalités de relations

        Accéder à mon profil: https://lexikon.chessplorer.com/profile

        L'équipe Lexikon
        https://lexikon.chessplorer.com
        """

        return EmailService._send_email(email, subject, html_content, text_content)

    @staticmethod
    def send_verification_email(email: str, first_name: str, verification_token: str) -> bool:
        """Send email verification link."""
        subject = "Vérifiez votre adresse email"
        verification_url = f"https://lexikon.chessplorer.com/verify-email?token={verification_token}"

        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h1 style="color: #2563eb;">Vérifiez votre adresse email</h1>

                    <p>Bonjour {first_name},</p>

                    <p>Pour finir de configurer votre compte Lexikon, veuillez vérifier votre adresse email en cliquant sur le lien ci-dessous:</p>

                    <p>
                        <a href="{verification_url}"
                           style="background-color: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block;">
                            Vérifier mon email
                        </a>
                    </p>

                    <p style="color: #666; font-size: 12px;">
                        Ou copiez ce lien dans votre navigateur:<br>
                        <code>{verification_url}</code>
                    </p>

                    <p style="color: #999; font-size: 12px;">
                        Ce lien expire dans 24 heures.
                    </p>

                    <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;">

                    <p style="font-size: 12px; color: #666;">
                        L'équipe Lexikon
                    </p>
                </div>
            </body>
        </html>
        """

        text_content = f"""
        Vérifiez votre adresse email

        Bonjour {first_name},

        Pour finir de configurer votre compte Lexikon, vérifiez votre adresse email:
        {verification_url}

        Ce lien expire dans 24 heures.

        L'équipe Lexikon
        """

        return EmailService._send_email(email, subject, html_content, text_content)

    @staticmethod
    def send_password_reset_email(email: str, first_name: str, reset_token: str) -> bool:
        """Send password reset email."""
        subject = "Réinitialisez votre mot de passe Lexikon"
        reset_url = f"https://lexikon.chessplorer.com/reset-password?token={reset_token}"

        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h1 style="color: #2563eb;">Réinitialisez votre mot de passe</h1>

                    <p>Bonjour {first_name},</p>

                    <p>Vous avez demandé la réinitialisation de votre mot de passe. Cliquez sur le lien ci-dessous pour continuer:</p>

                    <p>
                        <a href="{reset_url}"
                           style="background-color: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block;">
                            Réinitialiser mon mot de passe
                        </a>
                    </p>

                    <p style="color: #666; font-size: 12px;">
                        Ou copiez ce lien dans votre navigateur:<br>
                        <code>{reset_url}</code>
                    </p>

                    <p style="color: #d32f2f; font-size: 12px;">
                        <strong>⚠️ Attention:</strong> Ce lien expire dans 1 heure et ne peut être utilisé qu'une seule fois.
                    </p>

                    <p style="color: #999; font-size: 12px;">
                        Si vous n'avez pas demandé cette réinitialisation, ignorez cet email. Votre compte reste sécurisé.
                    </p>

                    <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;">

                    <p style="font-size: 12px; color: #666;">
                        L'équipe Lexikon
                    </p>
                </div>
            </body>
        </html>
        """

        text_content = f"""
        Réinitialisez votre mot de passe

        Bonjour {first_name},

        Vous avez demandé la réinitialisation de votre mot de passe. Cliquez sur le lien ci-dessous:
        {reset_url}

        ⚠️ ATTENTION: Ce lien expire dans 1 heure.

        Si vous n'avez pas demandé cette réinitialisation, ignorez cet email.

        L'équipe Lexikon
        """

        return EmailService._send_email(email, subject, html_content, text_content)


# Singleton instance
email_service = EmailService()
