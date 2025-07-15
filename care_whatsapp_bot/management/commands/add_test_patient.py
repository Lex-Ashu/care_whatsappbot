from django.core.management.base import BaseCommand
from django.utils import timezone
from care.emr.models.patient import Patient
from care.facility.models import Organization
import uuid


class Command(BaseCommand):
    help = 'Add a test patient for WhatsApp bot testing'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--phone',
            type=str,
            required=True,
            help='Phone number of the patient (e.g., +918767341918)'
        )
        parser.add_argument(
            '--name',
            type=str,
            default='Test Patient',
            help='Name of the patient'
        )
        parser.add_argument(
            '--age',
            type=int,
            default=25,
            help='Age of the patient'
        )
    
    def handle(self, *args, **options):
        phone_number = options['phone']
        name = options['name']
        age = options['age']
        
        # Normalize phone number
        normalized_phone = ''.join(filter(str.isdigit, phone_number))
        if len(normalized_phone) == 10:
            normalized_phone = f"91{normalized_phone}"
        elif normalized_phone.startswith('0'):
            normalized_phone = f"91{normalized_phone[1:]}"
        
        # Check if patient already exists
        existing_patient = Patient.objects.filter(
            phone_number__icontains=normalized_phone[-10:]
        ).first()
        
        if existing_patient:
            self.stdout.write(
                self.style.WARNING(
                    f'Patient with phone {phone_number} already exists: {existing_patient.name}'
                )
            )
            return
        
        # Get or create default organization
        organization, created = Organization.objects.get_or_create(
            name='Test Hospital',
            defaults={
                'org_type': 'govt',
                'address': 'Test Address',
                'pincode': '123456',
                'phone_number': '1234567890'
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created test organization: {organization.name}')
            )
        
        # Create patient
        patient = Patient.objects.create(
            external_id=str(uuid.uuid4()),
            name=name,
            phone_number=normalized_phone,
            date_of_birth=timezone.now().date().replace(year=timezone.now().year - age),
            gender='M',  # Default to Male
            organization=organization,
            created_date=timezone.now(),
            modified_date=timezone.now()
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created patient:\n'
                f'  Name: {patient.name}\n'
                f'  Phone: {patient.phone_number}\n'
                f'  External ID: {patient.external_id}\n'
                f'  Organization: {patient.organization.name}\n'
                f'\nYou can now test the WhatsApp bot with phone number: {phone_number}'
            )
        )
        
        # Add some sample medical data
        self._add_sample_medical_data(patient)
    
    def _add_sample_medical_data(self, patient):
        """Add sample medical records for testing"""
        try:
            from care.emr.models.encounter import Encounter
            from care.emr.models.medication_request import MedicationRequest
            from care.facility.models import PatientConsultation
            
            # Create sample encounter
            encounter = Encounter.objects.create(
                patient=patient,
                status='finished',
                class_type='outpatient',
                period_start=timezone.now() - timezone.timedelta(days=7),
                period_end=timezone.now() - timezone.timedelta(days=6),
                created_date=timezone.now(),
                modified_date=timezone.now()
            )
            
            # Create sample medication request
            MedicationRequest.objects.create(
                patient=patient,
                encounter=encounter,
                status='active',
                intent='order',
                medication_display='Paracetamol 500mg',
                dosage_instruction='Take 1 tablet twice daily after meals',
                authored_on=timezone.now() - timezone.timedelta(days=5),
                created_date=timezone.now(),
                modified_date=timezone.now()
            )
            
            MedicationRequest.objects.create(
                patient=patient,
                encounter=encounter,
                status='active',
                intent='order',
                medication_display='Vitamin D3 1000 IU',
                dosage_instruction='Take 1 capsule daily with breakfast',
                authored_on=timezone.now() - timezone.timedelta(days=3),
                created_date=timezone.now(),
                modified_date=timezone.now()
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    'Added sample medical data:\n'
                    '  - 1 Encounter (Outpatient visit)\n'
                    '  - 2 Medication Requests (Paracetamol, Vitamin D3)'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(
                    f'Could not add sample medical data: {e}\n'
                    'Patient created successfully, but without sample records.'
                )
            )