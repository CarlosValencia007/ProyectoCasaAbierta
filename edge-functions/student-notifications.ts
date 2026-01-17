/**
 * Edge Function para envío de notificaciones a estudiantes usando SMTP directo (Deno)
 * 
 * Notifica a estudiantes cuando:
 * 1. Son agregados a una materia/curso
 * 2. Su asistencia es verificada
 * 
 * Compatible con Gmail, Outlook, Yahoo, etc.
 * 
 * Variables de entorno requeridas:
 * - SMTP_HOST: smtp.gmail.com
 * - SMTP_PORT: 465 (SSL/TLS directo, compatible con denomailer)
 * - SMTP_USER: tu-email@gmail.com
 * - SMTP_PASS: contraseña-de-aplicación
 * - SUPABASE_URL
 * - SUPABASE_SERVICE_ROLE_KEY
 */

import { serve } from 'https://deno.land/std@0.168.0/http/server.ts';
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';
import { SMTPClient } from 'https://deno.land/x/denomailer@1.6.0/mod.ts';

// Variables de entorno
const SMTP_HOST = Deno.env.get('SMTP_HOST') || 'smtp.gmail.com';
const SMTP_PORT = parseInt(Deno.env.get('SMTP_PORT') || '465');
const SMTP_USER = Deno.env.get('SMTP_USER') || '';
const SMTP_PASS = Deno.env.get('SMTP_PASS') || '';
const SUPABASE_URL = Deno.env.get('SUPABASE_URL');
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');
const EMAIL_FROM_NAME = Deno.env.get('EMAIL_FROM_NAME') || 'Sistema Académico';

// Interfaces
interface StudentEnrollment {
  id: number;
  student_id: string;
  course_id: string;
  enrolled_at: string;
  students: {
    student_id: string;
    name: string;
    email: string | null;
  };
  courses?: {
    id: string;
    course_name: string;
    course_code: string;
    description: string | null;
    teacher_id: string;
  };
}

interface StudentAttendance {
  id: number;
  student_id: string;
  class_id: string;
  status: string;
  timestamp: string;
  confidence: number | null;
  students: {
    student_id: string;
    name: string;
    email: string | null;
  };
}

/**
 * Genera un token único para confirmación de lectura.
 */
function generarTokenConfirmacion(): string {
  return crypto.randomUUID();
}

/**
 * Delay para evitar rate limiting.
 */
function delay(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

const DELAY_ENTRE_EMAILS = 1000;

/**
 * Formatea la fecha en español.
 */
function formatearFecha(fecha: string): string {
  const date = new Date(fecha);
  return date.toLocaleDateString('es-ES', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
}

/**
 * Formatea la hora en formato legible.
 */
function formatearHora(fecha: string): string {
  const date = new Date(fecha);
  const horas = date.getHours();
  const minutos = date.getMinutes().toString().padStart(2, '0');
  const periodo = horas >= 12 ? 'PM' : 'AM';
  const hora12 = horas > 12 ? horas - 12 : horas === 0 ? 12 : horas;
  return `${hora12}:${minutos} ${periodo}`;
}

/**
 * Genera el cuerpo del email HTML para inscripción a materia.
 */
function generarEmailInscripcion(
  enrollment: StudentEnrollment,
  tokenConfirmacion: string
): string {
  const student = enrollment.students;
  const course = enrollment.courses;
  
  return `<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: 'Segoe UI', Arial, sans-serif; background-color: #f4f4f4;">
<div style="max-width: 600px; margin: 0 auto; background-color: #ffffff;">
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center;">
<h1 style="color: white; margin: 0; font-size: 28px;">📚 ¡Bienvenido a tu nueva materia!</h1>
</div>
<div style="padding: 30px;">
<p style="font-size: 18px; color: #333;">Hola <strong>${student.name}</strong>,</p>
<p style="color: #555; line-height: 1.6;">Te informamos que has sido inscrito exitosamente en la siguiente materia:</p>
<div style="background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%); border-radius: 12px; padding: 25px; margin: 25px 0; border-left: 5px solid #667eea;">
${course ? `<h2 style="color: #667eea; margin-top: 0; margin-bottom: 15px;">📖 ${course.course_name}</h2>` : `<h2 style="color: #667eea; margin-top: 0; margin-bottom: 15px;">📖 Materia ID: ${enrollment.course_id}</h2>`}
<table style="width: 100%; border-collapse: collapse;">
${course?.course_code ? `<tr><td style="padding: 10px 0; vertical-align: top; width: 40px;"><span style="font-size: 24px;">🔢</span></td><td style="padding: 10px 0;"><strong style="color: #333;">Código del curso</strong><br><span style="color: #667eea; font-size: 16px;">${course.course_code}</span></td></tr>` : ''}
<tr><td style="padding: 10px 0; vertical-align: top; width: 40px;"><span style="font-size: 24px;">📝</span></td><td style="padding: 10px 0;"><strong style="color: #333;">Fecha de inscripción</strong><br><span style="color: #667eea; font-size: 16px;">${formatearFecha(enrollment.enrolled_at)}</span></td></tr>
</table>
</div>
<div style="background-color: #f8f9fa; border-radius: 8px; padding: 20px; margin: 20px 0;">
<h3 style="color: #333; margin-top: 0; font-size: 16px;">ℹ️ Información importante</h3>
<ul style="color: #666; line-height: 1.8; margin: 10px 0;">
<li>Tu asistencia será registrada mediante reconocimiento facial</li>
<li>Asegúrate de asistir puntualmente a las clases</li>
<li>Recibirás confirmación cada vez que se registre tu asistencia</li>
</ul>
</div>
</div>
<div style="background-color: #f8f9fa; padding: 20px; text-align: center; border-top: 1px solid #e9ecef;">
<p style="color: #6c757d; font-size: 12px; margin: 0;">Este correo fue enviado automáticamente por el Sistema de Gestión Académica.</p>
<p style="color: #6c757d; font-size: 12px; margin: 5px 0 0 0;">Si tienes preguntas, contacta a tu profesor o al departamento académico.</p>
</div>
</div>
</body>
</html>`;
}

/**
 * Genera el cuerpo del email HTML para confirmación de asistencia.
 */
function generarEmailAsistencia(
  attendance: StudentAttendance,
  tokenConfirmacion: string
): string {
  const student = attendance.students;
  
  const urlConfirmacion = `${SUPABASE_URL}/functions/v1/student-notifications-handler?token=${tokenConfirmacion}`;
  
  const statusConfig = {
    present: { icon: '✅', color: '#10b981', text: 'Presente', bg: '#d1fae5' },
    late: { icon: '⚠️', color: '#f59e0b', text: 'Tarde', bg: '#fef3c7' },
    absent: { icon: '❌', color: '#ef4444', text: 'Ausente', bg: '#fee2e2' }
  };
  
  const status = statusConfig[attendance.status as keyof typeof statusConfig] || statusConfig.present;
  
  return `<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: 'Segoe UI', Arial, sans-serif; background-color: #f4f4f4;">
<div style="max-width: 600px; margin: 0 auto; background-color: #ffffff;">
<div style="background: linear-gradient(135deg, ${status.color} 0%, ${status.color}dd 100%); padding: 30px; text-align: center;">
<h1 style="color: white; margin: 0; font-size: 28px;">${status.icon} Asistencia Registrada</h1>
</div>
<div style="padding: 30px;">
<p style="font-size: 18px; color: #333;">Hola <strong>${student.name}</strong>,</p>
<p style="color: #555; line-height: 1.6;">Tu asistencia ha sido verificada exitosamente mediante reconocimiento facial.</p>
<div style="background-color: ${status.bg}; border: 2px solid ${status.color}; border-radius: 12px; padding: 20px; margin: 25px 0; text-align: center;">
<div style="font-size: 48px; margin-bottom: 10px;">${status.icon}</div>
<h2 style="color: ${status.color}; margin: 0; font-size: 24px;">Estado: ${status.text}</h2>
</div>
<div style="background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%); border-radius: 12px; padding: 25px; margin: 25px 0; border-left: 5px solid #667eea;">
<h3 style="color: #667eea; margin-top: 0; margin-bottom: 15px;">📚 Clase: ${attendance.class_id}</h3>
<table style="width: 100%; border-collapse: collapse;">
<tr><td style="padding: 10px 0; vertical-align: top; width: 40px;"><span style="font-size: 24px;">🕐</span></td><td style="padding: 10px 0;"><strong style="color: #333;">Hora de registro</strong><br><span style="color: #667eea; font-size: 16px;">${formatearFecha(attendance.timestamp)} a las ${formatearHora(attendance.timestamp)}</span></td></tr>
${attendance.confidence ? `<tr><td style="padding: 10px 0; vertical-align: top;"><span style="font-size: 24px;">🎯</span></td><td style="padding: 10px 0;"><strong style="color: #333;">Confianza de reconocimiento</strong><br><span style="color: #667eea; font-size: 16px;">${(attendance.confidence * 100).toFixed(1)}%</span></td></tr>` : ''}
</table>
</div>
${attendance.status === 'late' ? `<div style="background-color: #fef3c7; border-left: 4px solid #f59e0b; border-radius: 8px; padding: 20px; margin: 20px 0;"><p style="color: #92400e; margin: 0; line-height: 1.6;"><strong>⚠️ Llegada tarde:</strong> Te recomendamos llegar puntualmente a las próximas clases.</p></div>` : attendance.status === 'absent' ? `<div style="background-color: #fee2e2; border-left: 4px solid #ef4444; border-radius: 8px; padding: 20px; margin: 20px 0;"><p style="color: #991b1b; margin: 0; line-height: 1.6;"><strong>❌ Ausencia registrada:</strong> Si consideras que esto es un error, contacta a tu profesor.</p></div>` : `<div style="background-color: #d1fae5; border-left: 4px solid #10b981; border-radius: 8px; padding: 20px; margin: 20px 0;"><p style="color: #065f46; margin: 0; line-height: 1.6;"><strong>✅ ¡Excelente!</strong> Tu asistencia ha sido registrada correctamente.</p></div>`}
</html>`;
}

/**
 * Envía un email usando SMTP directo con denomailer.
 */
async function enviarEmailSMTP(
  destinatario: string,
  asunto: string,
  cuerpoHtml: string
): Promise<{ exito: boolean; messageId?: string; error?: string }> {
  
  const client = new SMTPClient({
    connection: {
      hostname: SMTP_HOST,
      port: SMTP_PORT,
      tls: true,
      auth: {
        username: SMTP_USER,
        password: SMTP_PASS,
      },
    },
  });

  try {
    await client.send({
      from: `${EMAIL_FROM_NAME} <${SMTP_USER}>`,
      to: destinatario,
      subject: asunto,
      content: "Por favor usa un cliente de correo compatible con HTML",
      html: cuerpoHtml,
    });

    await client.close();
    
    return { 
      exito: true, 
      messageId: `smtp-${Date.now()}` 
    };
  } catch (error) {
    await client.close();
    console.error('Error SMTP:', error);
    return { 
      exito: false, 
      error: error.message 
    };
  }
}

serve(async (req) => {
  try {
    // Verificar configuración SMTP
    if (!SMTP_USER || !SMTP_PASS) {
      return new Response(JSON.stringify({
        error: 'SMTP no configurado. Configura SMTP_USER y SMTP_PASS en los secrets.'
      }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    if (req.method !== 'POST' && req.method !== 'GET') {
      return new Response(JSON.stringify({
        error: 'Método no permitido'
      }), {
        status: 405,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    const supabase = createClient(SUPABASE_URL!, SUPABASE_SERVICE_ROLE_KEY!);
    const ahora = new Date();
    
    const url = new URL(req.url);
    const accion = url.searchParams.get('accion') || 'nuevas_inscripciones';

    console.log(`🚀 Iniciando proceso: ${accion}`);
    console.log(`📧 SMTP: ${SMTP_HOST}:${SMTP_PORT}`);

    let emailCounter = 0;

    const notificacionesEnviadas: Array<{
      student_id: string;
      email: string;
      message_id: string;
      tipo: string;
    }> = [];
    const errores: Array<{
      student_id: string;
      error: unknown;
    }> = [];

    if (accion === 'nuevas_inscripciones') {
      // === NOTIFICAR NUEVAS INSCRIPCIONES ===
      console.log('🔍 Buscando nuevas inscripciones...');

      // Obtener inscripciones que aún no han sido notificadas
      const { data: enrollments, error: errorEnrollments } = await supabase
        .from('enrollments')
        .select(`
          id,
          student_id,
          course_id,
          enrolled_at,
          students!inner(
            student_id,
            name,
            email
          ),
          courses(
            id,
            course_name,
            course_code,
            description,
            teacher_id
          )
        `)
        .not('students.email', 'is', null)
        .order('enrolled_at', { ascending: false });

      if (errorEnrollments) {
        throw errorEnrollments;
      }

      // Verificar cuáles ya tienen notificación
      const { data: notificacionesExistentes } = await supabase
        .from('student_notifications')
        .select('reference_id, notification_type')
        .eq('notification_type', 'enrollment');

      const idsConNotificacion = new Set(
        notificacionesExistentes?.map(n => n.reference_id) || []
      );

      const enrollmentsSinNotificar = (enrollments || []).filter(
        enr => !idsConNotificacion.has(enr.id)
      );

      console.log(`📊 ${enrollmentsSinNotificar.length} inscripciones nuevas`);

      if (enrollmentsSinNotificar.length === 0) {
        return new Response(JSON.stringify({
          mensaje: 'No hay nuevas inscripciones para notificar',
          cantidad: 0
        }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' }
        });
      }

      for (const enrollment of enrollmentsSinNotificar) {
        try {
          const student = enrollment.students;
          
          if (!student.email) {
            console.log(`⏭️ Estudiante ${student.student_id} sin email`);
            continue;
          }

          // Delay entre emails
          if (emailCounter > 0) {
            await delay(DELAY_ENTRE_EMAILS);
          }
          emailCounter++;

          const tokenConfirmacion = generarTokenConfirmacion();
          const asunto = `📚 ¡Has sido inscrito en ${enrollment.courses?.course_name || 'una nueva materia'}!`;
          const cuerpoEmail = generarEmailInscripcion(enrollment, tokenConfirmacion);

          console.log(`📧 Enviando a ${student.email}...`);
          const resultado = await enviarEmailSMTP(student.email, asunto, cuerpoEmail);

          if (!resultado.exito) {
            console.error(`❌ Error:`, resultado.error);
            errores.push({ student_id: student.student_id, error: resultado.error });
            continue;
          }

          console.log(`✅ Enviado: ${resultado.messageId}`);

          // Registrar notificación
          await supabase
            .from('student_notifications')
            .insert({
              student_id: student.student_id,
              notification_type: 'enrollment',
              reference_id: enrollment.id,
              email_sent: student.email,
              sent_at: ahora.toISOString(),
              is_read: false,
              confirmation_token: tokenConfirmacion
            });

          notificacionesEnviadas.push({
            student_id: student.student_id,
            email: student.email,
            message_id: resultado.messageId!,
            tipo: 'enrollment'
          });
        } catch (error) {
          errores.push({ student_id: enrollment.student_id, error: error.message });
        }
      }
    } else if (accion === 'nuevas_asistencias') {
      // === NOTIFICAR NUEVAS ASISTENCIAS ===
      console.log('🔍 Buscando nuevas asistencias verificadas...');

      // Obtener asistencias recientes que no han sido notificadas
      const { data: attendances, error: errorAttendances } = await supabase
        .from('attendance')
        .select(`
          id,
          student_id,
          class_id,
          status,
          timestamp,
          confidence,
          students!inner(
            student_id,
            name,
            email
          )
        `)
        .not('students.email', 'is', null)
        .order('timestamp', { ascending: false });

      if (errorAttendances) {
        throw errorAttendances;
      }

      // Verificar cuáles ya tienen notificación
      const { data: notificacionesExistentes } = await supabase
        .from('student_notifications')
        .select('reference_id, notification_type')
        .eq('notification_type', 'attendance');

      const idsConNotificacion = new Set(
        notificacionesExistentes?.map(n => n.reference_id) || []
      );

      const attendancesSinNotificar = (attendances || []).filter(
        att => !idsConNotificacion.has(att.id)
      );

      console.log(`📊 ${attendancesSinNotificar.length} asistencias nuevas`);

      if (attendancesSinNotificar.length === 0) {
        return new Response(JSON.stringify({
          mensaje: 'No hay nuevas asistencias para notificar',
          cantidad: 0
        }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' }
        });
      }

      for (const attendance of attendancesSinNotificar) {
        try {
          const student = attendance.students;
          
          if (!student.email) {
            console.log(`⏭️ Estudiante ${student.student_id} sin email`);
            continue;
          }

          // Delay entre emails
          if (emailCounter > 0) {
            await delay(DELAY_ENTRE_EMAILS);
          }
          emailCounter++;

          const tokenConfirmacion = generarTokenConfirmacion();
          const statusText = {
            present: '✅ Presente',
            late: '⚠️ Tarde',
            absent: '❌ Ausente'
          }[attendance.status] || '✅ Verificada';
          
          const asunto = `${statusText} - Asistencia registrada en clase ${attendance.class_id}`;
          const cuerpoEmail = generarEmailAsistencia(attendance, tokenConfirmacion);

          console.log(`📧 Enviando a ${student.email}...`);
          const resultado = await enviarEmailSMTP(student.email, asunto, cuerpoEmail);

          if (!resultado.exito) {
            console.error(`❌ Error:`, resultado.error);
            errores.push({ student_id: student.student_id, error: resultado.error });
            continue;
          }

          console.log(`✅ Enviado: ${resultado.messageId}`);

          // Registrar notificación
          await supabase
            .from('student_notifications')
            .insert({
              student_id: student.student_id,
              notification_type: 'attendance',
              reference_id: attendance.id,
              email_sent: student.email,
              sent_at: ahora.toISOString(),
              is_read: false,
              confirmation_token: tokenConfirmacion
            });

          notificacionesEnviadas.push({
            student_id: student.student_id,
            email: student.email,
            message_id: resultado.messageId!,
            tipo: 'attendance'
          });
        } catch (error) {
          errores.push({ student_id: attendance.student_id, error: error.message });
        }
      }
    } else {
      return new Response(JSON.stringify({
        error: 'Acción no válida. Usa: nuevas_inscripciones o nuevas_asistencias'
      }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    console.log(`✅ Completado: ${notificacionesEnviadas.length} enviados, ${errores.length} errores`);

    return new Response(JSON.stringify({
      exito: true,
      mensaje: 'Proceso completado',
      smtp: `${SMTP_HOST}:${SMTP_PORT}`,
      notificaciones_enviadas: notificacionesEnviadas.length,
      errores: errores.length,
      detalles: {
        notificaciones: notificacionesEnviadas,
        errores
      }
    }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (error) {
    console.error('❌ Error fatal:', error);
    return new Response(JSON.stringify({
      error: error.message,
      stack: error.stack
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
});
