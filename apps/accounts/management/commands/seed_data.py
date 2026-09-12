import random
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import StaffProfile
from apps.bookings.models import Booking
from apps.clients.models import Client
from apps.equipment.models import Equipment
from apps.expenses.models import Expense, ExpenseCategory
from apps.finance.models import Invoice, InvoiceItem, Payment
from apps.gallery.models import Gallery, Photo
from apps.inventory.models import InventoryItem, StockTransaction
from apps.leads.models import Lead
from apps.notifications.models import Notification
from apps.packages.models import Package, ServiceCategory
from apps.printing.models import AlbumOrder, FrameOrder, PrintJob
from apps.projects.models import Project, ProjectTask
from apps.studios.models import Studio

User = get_user_model()

FIRST_NAMES = [
    "Adaeze", "Chidinma", "Emeka", "Fatima", "Ibrahim", "Chukwuemeka",
    "Ngozi", "Oluwaseun", "Amina", "Tunde", "Chioma", "Abdul",
    "Blessing", "Kenneth", "Yemi", "Hauwa", "Femi", "Ifeanyi",
    "Zainab", "Obinna", "Grace", "Sunday", "Amara", "Chinedu",
    "Blessing", "Uche", "Funke", "Segun", "Nneka", "Adeola",
    "Kemi", "Chidi", "Aisha", "Bayo", "Nneka", "Emmanuel",
]

LAST_NAMES = [
    "Okafor", "Adeyemi", "Ibrahim", "Nwosu", "Bello", "Chukwuma",
    "Mohammed", "Obi", "Adeleke", "Eze", "Okonkwo", "Abubakar",
    "Akinwale", "Ogundimu", "Aliyu", "Nnamdi", "Bakare", "Ugwu",
    "Lawal", "Chineke", "Olumide", "Yusuf", "Onwueme", "Adewale",
    "Adekunle", "Iheanacho", "Suleiman", "Ogundele", "Chizoba", "Danjuma",
]

EVENT_TYPES = [
    "Wedding", "Pre-wedding", "Traditional Marriage", "Engagement",
    "Birthday", "Chistinening", "Corporation", "Product Shoot",
    "Family Portrait", "Maternity", "Graduation", "Headshot",
]

LOCATIONS = [
    "Studio A", "Studio B", "Lekki Beach", "Ikoyi Gardens",
    "Eko Hotel", "Federal Palace Hotel", "Oriental Hotel",
    "Freedom Park", "Muri Okunola Park", "Private Residence",
]

SOURCES = [
    "Instagram", "Facebook", "Referral", "Walk-in", "Google Search",
    "WhatsApp", "Wedding Plan", "Tunde Event", "Website",
]

VENDORS = [
    "Photo Kong", "Kingdom Photo", "PrintWorx", "Frame Nigeria",
    "Album Masters", "Studio Supplies Lagos", "Jumia", "Konga",
]

INVENTORY_ITEMS = [
    ("INK-001", "Canon CLI-526 Ink Cartridge", "Printing", 25, "pcs", 5, Decimal("8500")),
    ("PAP-001", "A4 Glossy Photo Paper", "Paper", 100, "sheets", 20, Decimal("350")),
    ("PAP-002", "A3 Matte Photo Paper", "Paper", 50, "sheets", 10, Decimal("600")),
    ("PAP-003", "5x7 Lustre Print Paper", "Paper", 200, "sheets", 30, Decimal("200")),
    ("PAP-004", "8x10 Fine Art Paper", "Paper", 40, "sheets", 10, Decimal("900")),
    ("FRM-001", "8x10 Black Frame", "Frames", 15, "pcs", 5, Decimal("3500")),
    ("FRM-002", "12x16 Gold Frame", "Frames", 8, "pcs", 3, Decimal("5500")),
    ("FRM-003", "16x20 White Frame", "Frames", 6, "pcs", 2, Decimal("7500")),
    ("ALB-001", "20-page Leather Album", "Albums", 5, "pcs", 2, Decimal("25000")),
    ("ALB-002", "30-page Linen Album", "Albums", 3, "pcs", 1, Decimal("35000")),
    ("BTR-001", "Canon LP-E6 Battery", "Batteries", 10, "pcs", 3, Decimal("12000")),
    ("SDC-001", "64GB SD Card", "Storage", 8, "pcs", 3, Decimal("8500")),
    ("SDC-002", "128GB CF Express Card", "Storage", 4, "pcs", 2, Decimal("25000")),
    ("LGT-001", "Godox AD200 Flash", "Lighting", 4, "pcs", 2, Decimal("95000")),
    ("LGT-002", "Softbox 60x90cm", "Lighting", 6, "pcs", 2, Decimal("15000")),
    ("USB-001", "SanDisk 1TB SSD", "Storage", 3, "pcs", 1, Decimal("65000")),
    ("CLN-001", "Sensor Cleaning Kit", "Maintenance", 2, "sets", 1, Decimal("5000")),
    ("BKG-001", "White Background Paper Roll", "Backgrounds", 5, "rolls", 2, Decimal("8000")),
    ("BKG-002", "Black Background Paper Roll", "Backgrounds", 4, "rolls", 2, Decimal("8000")),
    ("MNT-001", "Monitor Calibration Tool", "Accessories", 1, "pcs", 1, Decimal("45000")),
]

EQUIPMENT_ITEMS = [
    ("EQ-001", "Canon EOS R5", "Canon", "EOS R5", "RF12345678", Decimal("2800000")),
    ("EQ-002", "Canon EOS R6 Mark II", "Canon", "EOS R6 II", "RF87654321", Decimal("1800000")),
    ("EQ-003", "Nikon Z6 III", "Nikon", "Z6 III", "NK11223344", Decimal("1500000")),
    ("EQ-004", "Sony A7 IV", "Sony", "A7 IV", "SN55667788", Decimal("1600000")),
    ("EQ-005", "Canon RF 24-70mm f/2.8L", "Canon", "RF 24-70 f/2.8", "LNS1122334", Decimal("950000")),
    ("EQ-006", "Canon RF 70-200mm f/2.8L", "Canon", "RF 70-200 f/2.8", "LNS5566778", Decimal("1100000")),
    ("EQ-007", "Nikon Z 24-70mm f/2.8 S", "Nikon", "Z 24-70 f/2.8", "LNS9988776", Decimal("850000")),
    ("EQ-008", "Godox AD600Pro", "Godox", "AD600Pro", "FL12345678", Decimal("350000")),
    ("EQ-009", "DJI Mavic 3 Pro", "DJI", "Mavic 3 Pro", "DR23456789", Decimal("950000")),
    ("EQ-010", "Manfrotto 055 Tripod", "Manfrotto", "MT055XPRO3", "TR11223344", Decimal("120000")),
    ("EQ-011", "Blackmagic Pocket 6K", "Blackmagic", "Pocket 6K", "BM98765432", Decimal("1200000")),
    ("EQ-012", "Dell UltraSharp 27 Monitor", "Dell", "U2723QE", "MN55443322", Decimal("280000")),
]


def _date(days_ago):
    return date.today() - timedelta(days=days_ago)


def _future_date(days_ahead):
    return date.today() + timedelta(days=days_ahead)


def _dt(days_ago, hour=10):
    return timezone.now() - timedelta(days=days_ago, hours=hour)


class Command(BaseCommand):
    help = "Seed the database with sample data for StudioFlow"

    def handle(self, *args, **options):
        self.stdout.write("Seeding StudioFlow database...")

        studio = self._create_studio()
        users = self._create_users(studio)
        owner = users[0]
        photographer = users[1] if len(users) > 1 else owner
        editor = users[2] if len(users) > 2 else owner

        categories = self._create_categories(studio)
        packages = self._create_packages(studio, categories)
        clients = self._create_clients(studio, users)
        leads = self._create_leads(studio, users)
        bookings = self._create_bookings(studio, clients, packages, photographer, owner)
        projects = self._create_projects(studio, clients, bookings, packages, photographer, editor, owner)
        self._create_galleries(projects)
        invoices = self._create_invoices(studio, clients, bookings, projects)
        self._create_payments(studio, clients, invoices, bookings, owner)
        expense_cats = self._create_expense_categories(studio)
        self._create_expenses(studio, expense_cats, projects, owner)
        self._create_inventory(studio, owner)
        self._create_equipment(studio, users)
        self._create_printing(projects, clients)
        self._create_notifications(users)

        self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))

    def _create_studio(self):
        studio, _ = Studio.objects.get_or_create(
            name="Lagos Photography Studio",
            defaults={
                "phone": "+234 801 234 5678",
                "whatsapp": "+234 801 234 5678",
                "email": "info@lagosstudio.com",
                "website": "https://lagosstudio.com",
                "address": "15 Admiralty Way, Lekki Phase 1",
                "city": "Lagos",
                "state": "Lagos",
                "country": "Nigeria",
                "currency": "NGN",
                "tax_rate": Decimal("7.50"),
                "default_deposit_percentage": Decimal("50.00"),
            },
        )
        self.stdout.write(f"  Studio: {studio.name}")
        return studio

    def _create_users(self, studio):
        user_data = [
            ("admin@lagosstudio.com", "Admin", "Owner", "owner", True),
            (" photographers@lagosstudio.com", "Tunde", "Adeyemi", "photographer", True),
            ("editor@lagosstudio.com", "Chioma", "Okafor", "photo_editor", True),
            ("reception@lagosstudio.com", "Amina", "Ibrahim", "receptionist", True),
            ("accounts@lagosstudio.com", "Femi", "Bakare", "accountant", True),
            ("printing@lagosstudio.com", "Emeka", "Nwosu", "printing_staff", True),
        ]
        users = []
        for email, first, last, role, is_staff in user_data:
            email = email.strip()
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "first_name": first,
                    "last_name": last,
                    "is_staff": is_staff,
                    "studio": studio,
                },
            )
            if created:
                user.set_password("studio123")
                user.save()
            StaffProfile.objects.get_or_create(
                user=user,
                defaults={
                    "studio": studio,
                    "role": role,
                    "job_title": role.replace("_", " ").title(),
                    "phone": f"+234 80{random.randint(10,99)} {random.randint(100,999)} {random.randint(1000,9999)}",
                    "hire_date": _date(random.randint(100, 800)),
                },
            )
            users.append(user)
        self.stdout.write(f"  Users: {len(users)}")
        return users

    def _create_categories(self, studio):
        cat_data = ["Wedding", "Portrait", "Event", "Commercial", "Family"]
        categories = []
        for name in cat_data:
            cat, _ = ServiceCategory.objects.get_or_create(
                studio=studio, name=name, defaults={"description": f"{name} photography services"}
            )
            categories.append(cat)
        self.stdout.write(f"  Categories: {len(categories)}")
        return categories

    def _create_packages(self, studio, categories):
        pkg_data = [
            ("Classic Wedding", categories[0], Decimal("350000"), "Full day wedding coverage with 2 photographers"),
            ("Premium Wedding", categories[0], Decimal("650000"), "Full day coverage, 2 photographers, video highlights"),
            ("Royal Wedding", categories[0], Decimal("1200000"), "Two-day coverage, drone, same-day edit, album"),
            ("Portrait Basic", categories[1], Decimal("50000"), "30-minute session, 10 edited images"),
            ("Portrait Premium", categories[1], Decimal("120000"), "1-hour session, 25 edited images, 1 print"),
            ("Corporate Headshot", categories[1], Decimal("30000"), "15-minute session, 3 edited headshots"),
            ("Birthday Bash", categories[2], Decimal("150000"), "3-hour event coverage, 50 edited images"),
            ("Birthday Deluxe", categories[2], Decimal("250000"), "5-hour coverage, 80 images, photo booth"),
            ("Product Shoot", categories[3], Decimal("80000"), "Up to 20 products, white background"),
            ("Brand Campaign", categories[3], Decimal("500000"), "Full day, location shoot, creative direction"),
            ("Family Portrait", categories[4], Decimal("75000"), "1-hour session, 20 edited images"),
            ("Extended Family", categories[4], Decimal("150000"), "2-hour session, 40 images, group shots"),
        ]
        packages = []
        for name, cat, price, desc in pkg_data:
            pkg, _ = Package.objects.get_or_create(
                studio=studio,
                name=name,
                defaults={
                    "category": cat,
                    "description": desc,
                    "price": price,
                    "deposit_percentage": Decimal("50.00"),
                    "duration_hours": Decimal(str(random.choice([1, 2, 3, 4, 6, 8]))),
                    "outfit_changes": random.randint(1, 3),
                    "edited_images": random.randint(10, 80),
                    "prints_included": random.randint(0, 5),
                    "delivery_estimate_days": random.choice([7, 14, 21, 30]),
                    "digital_files_included": True,
                    "is_active": True,
                    "is_featured": random.choice([True, False]),
                },
            )
            packages.append(pkg)
        self.stdout.write(f"  Packages: {len(packages)}")
        return packages

    def _create_clients(self, studio, users):
        clients = []
        for i in range(20):
            fn = random.choice(FIRST_NAMES)
            ln = random.choice(LAST_NAMES)
            client, _ = Client.objects.get_or_create(
                studio=studio,
                client_number=f"CLI-{i+1:03d}",
                defaults={
                    "first_name": fn,
                    "last_name": ln,
                    "phone": f"+234 80{random.randint(10,99)} {random.randint(100,999)} {random.randint(1000,9999)}",
                    "whatsapp": f"+234 80{random.randint(10,99)} {random.randint(100,999)} {random.randint(1000,9999)}",
                    "email": f"{fn.lower()}.{ln.lower()}@email.com",
                    "address": f"{random.randint(1,100)} {random.choice(['Adetokunbo', 'Herbert', 'Bourdillon', 'Ozumba', 'Adeola'])} Street",
                    "city": random.choice(["Lagos", "Abuja", "Port Harcourt", "Ibadan"]),
                    "state": random.choice(["Lagos", "FCT", "Rivers", "Oyo"]),
                    "referral_source": random.choice(SOURCES),
                    "assigned_to": random.choice(users[:4]),
                    "status": "active",
                },
            )
            clients.append(client)
        self.stdout.write(f"  Clients: {len(clients)}")
        return clients

    def _create_leads(self, studio, users):
        leads = []
        for i in range(15):
            fn = random.choice(FIRST_NAMES)
            ln = random.choice(LAST_NAMES)
            status = random.choice(["new", "contacted", "follow_up", "quotation_sent", "negotiating", "won", "lost"])
            lead, _ = Lead.objects.get_or_create(
                studio=studio,
                name=f"{fn} {ln}",
                defaults={
                    "phone": f"+234 80{random.randint(10,99)} {random.randint(100,999)} {random.randint(1000,9999)}",
                    "email": f"{fn.lower()}.{ln.lower()}@email.com",
                    "event_type": random.choice(EVENT_TYPES),
                    "expected_date": _future_date(random.randint(7, 90)),
                    "estimated_budget": Decimal(str(random.choice([100000, 150000, 250000, 350000, 500000, 800000]))),
                    "source": random.choice(SOURCES),
                    "assigned_to": random.choice(users[:4]),
                    "status": status,
                    "next_follow_up": _dt(random.randint(0, 5)) if status not in ("won", "lost") else None,
                },
            )
            leads.append(lead)
        self.stdout.write(f"  Leads: {len(leads)}")
        return leads

    def _create_bookings(self, studio, clients, packages, photographer, creator):
        bookings = []
        statuses = ["enquiry", "tentative", "awaiting_deposit", "confirmed", "in_progress", "completed", "cancelled"]
        for i in range(15):
            client = clients[i % len(clients)]
            pkg = packages[i % len(packages)]
            status = random.choice(statuses)
            total = pkg.price
            deposit = total * pkg.deposit_percentage / Decimal("100")
            paid = Decimal("0")
            if status in ("confirmed", "in_progress", "completed"):
                paid = deposit
            elif status == "partial":
                paid = deposit / Decimal("2")

            booking, _ = Booking.objects.get_or_create(
                studio=studio,
                reference=f"BKG-{i+1:03d}",
                defaults={
                    "client": client,
                    "package": pkg,
                    "title": f"{client.first_name}'s {pkg.name}",
                    "event_type": random.choice(EVENT_TYPES),
                    "date": _future_date(random.randint(-30, 60)),
                    "start_time": f"{random.choice([8,9,10,11,14,15])}:00",
                    "end_time": f"{random.choice([12,13,14,15,17,18])}:00",
                    "location": random.choice(LOCATIONS),
                    "location_type": random.choice(["studio", "outdoor", "event"]),
                    "photographer": photographer,
                    "base_price": total,
                    "total_amount": total,
                    "deposit_required": deposit,
                    "amount_paid": paid,
                    "balance": total - paid,
                    "payment_status": "paid" if paid >= total else ("partial" if paid > 0 else "unpaid"),
                    "status": status,
                    "special_instructions": random.choice([
                        "", "Outdoor shots preferred", "Bring extra outfit",
                        "Family group photos needed", "Morning ceremony only",
                    ]),
                    "created_by": creator,
                },
            )
            bookings.append(booking)
        self.stdout.write(f"  Bookings: {len(bookings)}")
        return bookings

    def _create_projects(self, studio, clients, bookings, packages, photographer, editor, pm):
        projects = []
        statuses = ["scheduled", "shoot_completed", "files_imported", "editing", "ready_for_delivery", "completed"]
        for i in range(10):
            client = clients[i % len(clients)]
            booking = bookings[i] if i < len(bookings) else None
            pkg = packages[i % len(packages)] if packages else None
            status = random.choice(statuses)
            project, _ = Project.objects.get_or_create(
                studio=studio,
                reference=f"PRJ-{i+1:03d}",
                defaults={
                    "client": client,
                    "booking": booking,
                    "package": pkg,
                    "photographer": photographer,
                    "editor": editor,
                    "project_manager": pm,
                    "shoot_date": _date(random.randint(0, 30)) if status != "scheduled" else _future_date(7),
                    "expected_delivery": _future_date(random.randint(7, 30)),
                    "status": status,
                    "priority": random.choice(["low", "medium", "high"]),
                    "total_captured": random.randint(50, 500) if status != "scheduled" else 0,
                    "total_for_selection": random.randint(20, 100) if status not in ("scheduled", "shoot_completed") else 0,
                    "selected_count": random.randint(10, 40) if status not in ("scheduled", "shoot_completed", "files_imported") else 0,
                    "edited_count": random.randint(5, 30) if status in ("editing", "ready_for_delivery", "completed") else 0,
                },
            )
            projects.append(project)
        self.stdout.write(f"  Projects: {len(projects)}")
        return projects

    def _create_galleries(self, projects):
        count = 0
        for project in projects[:6]:
            gallery, _ = Gallery.objects.get_or_create(
                project=project,
                name=f"{project.client.first_name}'s Gallery",
                defaults={
                    "description": "Client photo gallery",
                    "is_selection": True,
                    "is_published": project.status in ("ready_for_delivery", "completed"),
                },
            )
            for j in range(random.randint(5, 15)):
                Photo.objects.get_or_create(
                    gallery=gallery,
                    file_name=f"IMG_{project.reference}_{j+1:04d}.CR3",
                    defaults={
                        "storage_key": f"photos/{project.reference}/IMG_{j+1:04d}.CR3",
                        "image_number": j + 1,
                        "is_selected": random.choice([True, False]),
                        "is_edited": project.status in ("editing", "ready_for_delivery", "completed"),
                    },
                )
                count += 1
        self.stdout.write(f"  Galleries + Photos: {count}")

    def _create_invoices(self, studio, clients, bookings, projects):
        invoices = []
        for i in range(10):
            client = clients[i % len(clients)]
            booking = bookings[i] if i < len(bookings) else None
            project = projects[i] if i < len(projects) else None
            total = booking.total_amount if booking else Decimal(str(random.choice([100000, 200000, 350000, 500000])))
            amount_paid = total * Decimal(str(random.choice([0, 0.5, 0.75, 1.0])))
            status = "draft"
            if amount_paid >= total:
                status = "paid"
            elif amount_paid > 0:
                status = "partial"

            invoice, _ = Invoice.objects.get_or_create(
                studio=studio,
                invoice_number=f"INV-{i+1:03d}",
                defaults={
                    "client": client,
                    "booking": booking,
                    "project": project,
                    "issue_date": _date(random.randint(5, 30)),
                    "due_date": _future_date(random.randint(-10, 20)),
                    "subtotal": total,
                    "discount": Decimal("0"),
                    "tax": total * Decimal("0.075"),
                    "total": total * Decimal("1.075"),
                    "amount_paid": amount_paid,
                    "balance": total * Decimal("1.075") - amount_paid,
                    "status": status,
                    "notes": random.choice(["", "Payment due within 30 days", "Thank you for your business"]),
                },
            )
            InvoiceItem.objects.get_or_create(
                invoice=invoice,
                description=f"Photography services - {booking.title if booking else 'Studio session'}",
                defaults={
                    "quantity": Decimal("1"),
                    "unit_price": total,
                    "total": total,
                },
            )
            invoices.append(invoice)
        self.stdout.write(f"  Invoices: {len(invoices)}")
        return invoices

    def _create_payments(self, studio, clients, invoices, bookings, recorder):
        payments = []
        methods = ["cash", "bank_transfer", "pos", "card"]
        for i, invoice in enumerate(invoices):
            if invoice.amount_paid > 0:
                payment, _ = Payment.objects.get_or_create(
                    studio=studio,
                    reference=f"PAY-{i+1:03d}",
                    defaults={
                        "invoice": invoice,
                        "booking": invoice.booking,
                        "client": invoice.client,
                        "amount": invoice.amount_paid,
                        "payment_date": invoice.issue_date + timedelta(days=random.randint(0, 5)),
                        "method": random.choice(methods),
                        "recorded_by": recorder,
                        "notes": random.choice(["", "Full payment", "Deposit payment", "Balance payment"]),
                    },
                )
                payments.append(payment)
        self.stdout.write(f"  Payments: {len(payments)}")

    def _create_expense_categories(self, studio):
        cats = [
            "Rent", "Utilities", "Equipment Maintenance", "Printing Supplies",
            "Transportation", "Staff Welfare", "Marketing", "Software Subscriptions",
            "Studio Supplies", "Miscellaneous",
        ]
        categories = []
        for name in cats:
            cat, _ = ExpenseCategory.objects.get_or_create(studio=studio, name=name)
            categories.append(cat)
        self.stdout.write(f"  Expense Categories: {len(categories)}")
        return categories

    def _create_expenses(self, studio, categories, projects, recorder):
        expense_data = [
            (0, "Studio rent - Mainland", 250000),
            (1, "Electricity bill - PHCN", 45000),
            (2, "Canon R5 sensor cleaning", 15000),
            (3, "Glossy paper ream - Photo Kong", 12000),
            (4, "Fuel for client location shoot", 8000),
            (5, "Staff lunch - Team outing", 25000),
            (6, "Instagram ads - December campaign", 50000),
            (7, "Adobe Creative Cloud subscription", 35000),
            (8, "Background paper rolls", 16000),
            (9, "Miscellaneous expenses", 10000),
            (0, "Studio rent - Lekki office", 350000),
            (1, "Internet subscription - Spectranet", 20000),
            (3, "Frame supplies - Frame Nigeria", 45000),
            (4, "Uber for equipment delivery", 5000),
            (6, "Google Ads - Wedding season", 75000),
        ]
        for i, (cat_idx, desc, amount) in enumerate(expense_data):
            Expense.objects.get_or_create(
                studio=studio,
                reference=f"EXP-{i+1:03d}",
                defaults={
                    "category": categories[cat_idx],
                    "vendor": random.choice(VENDORS),
                    "description": desc,
                    "amount": Decimal(str(amount)),
                    "date": _date(random.randint(1, 60)),
                    "payment_method": random.choice(["cash", "transfer", "pos"]),
                    "project": random.choice(projects[:3]) if random.random() > 0.5 else None,
                    "entered_by": recorder,
                },
            )
        self.stdout.write(f"  Expenses: {len(expense_data)}")

    def _create_inventory(self, studio, recorder):
        for sku, name, cat, qty, unit, reorder, cost in INVENTORY_ITEMS:
            item, created = InventoryItem.objects.get_or_create(
                studio=studio,
                sku=sku,
                defaults={
                    "name": name,
                    "category": cat,
                    "quantity": qty,
                    "unit": unit,
                    "reorder_level": reorder,
                    "cost_price": cost,
                    "supplier": random.choice(VENDORS),
                    "location": random.choice(["Studio Storage", "Print Room", "Equipment Room", "Office"]),
                    "is_active": True,
                },
            )
            if created:
                StockTransaction.objects.get_or_create(
                    item=item,
                    transaction_type="in",
                    quantity=qty,
                    defaults={
                        "reference": f"SEED-{sku}",
                        "notes": "Initial stock",
                        "performed_by": recorder,
                    },
                )
        self.stdout.write(f"  Inventory: {len(INVENTORY_ITEMS)} items")

    def _create_equipment(self, studio, users):
        for asset, name, brand, model, serial, cost in EQUIPMENT_ITEMS:
            Equipment.objects.get_or_create(
                studio=studio,
                asset_number=asset,
                defaults={
                    "name": name,
                    "brand": brand,
                    "model_name": model,
                    "serial_number": serial,
                    "purchase_date": _date(random.randint(30, 365)),
                    "purchase_cost": cost,
                    "warranty_expiry": _future_date(random.randint(100, 700)),
                    "status": random.choice(["available", "available", "available", "in_use"]),
                    "assigned_to": random.choice(users[1:4]),
                    "condition_notes": random.choice(["", "Good condition", "Minor scratches", "New"]),
                    "next_maintenance": _future_date(random.randint(30, 180)),
                },
            )
        self.stdout.write(f"  Equipment: {len(EQUIPMENT_ITEMS)} items")

    def _create_printing(self, projects, clients):
        print_count = 0
        for project in projects[:5]:
            client = project.client
            for j in range(random.randint(1, 4)):
                PrintJob.objects.get_or_create(
                    project=project,
                    client=client,
                    print_size=random.choice(["5x7", "8x10", "11x14", "16x20"]),
                    defaults={
                        "quantity": random.randint(1, 5),
                        "paper_type": random.choice(["Glossy", "Matte", "Lustre", "Fine Art"]),
                        "vendor": random.choice(VENDORS[:4]),
                        "internal_cost": Decimal(str(random.choice([500, 1000, 1500, 2000]))),
                        "customer_price": Decimal(str(random.choice([1500, 2500, 3500, 5000]))),
                        "status": random.choice(["pending", "preparing", "sent", "ready", "delivered"]),
                        "due_date": _future_date(random.randint(3, 14)),
                    },
                )
                print_count += 1

        frame_count = 0
        for project in projects[:3]:
            FrameOrder.objects.get_or_create(
                project=project,
                size=random.choice(["8x10", "12x16", "16x20"]),
                defaults={
                    "frame_type": random.choice(["Classic Black", "Modern White", "Gold Ornate", "Wood"]),
                    "orientation": random.choice(["portrait", "landscape"]),
                    "quantity": random.randint(1, 3),
                    "supplier": "Frame Nigeria",
                    "internal_cost": Decimal(str(random.choice([3000, 5000, 7500]))),
                    "customer_price": Decimal(str(random.choice([8000, 12000, 18000]))),
                    "due_date": _future_date(random.randint(5, 21)),
                    "status": random.choice(["pending", "ordered", "received", "ready"]),
                },
            )
            frame_count += 1

        album_count = 0
        for project in projects[:2]:
            AlbumOrder.objects.get_or_create(
                project=project,
                defaults={
                    "album_type": random.choice(["Leather", "Linen", "Acrylic", "Canvas"]),
                    "size": random.choice(["10x10", "12x12", "8x8"]),
                    "pages": random.choice([20, 30, 40]),
                    "supplier": "Album Masters",
                    "cost": Decimal(str(random.choice([25000, 35000, 50000]))),
                    "selling_price": Decimal(str(random.choice([60000, 85000, 120000]))),
                    "delivery_date": _future_date(random.randint(14, 45)),
                    "design_status": random.choice(["pending", "designing", "review", "production"]),
                },
            )
            album_count += 1

        self.stdout.write(f"  Print Jobs: {print_count}, Frames: {frame_count}, Albums: {album_count}")

    def _create_notifications(self, users):
        notif_data = [
            ("booking_reminder", "Upcoming Wedding Shoot", "Adaeze Okafor's wedding shoot is in 3 days"),
            ("deposit_due", "Deposit Pending", "Ngozi Eze has not paid the deposit for BKG-005"),
            ("delivery_due", "Delivery Deadline", "Project PRJ-003 delivery is due tomorrow"),
            ("selection_ready", "Selection Ready", "Photos for Chidinma's portrait session are ready for selection"),
            ("payment_received", "Payment Received", "Payment of N175,000 received from Emeka Nwosu"),
            ("low_stock", "Low Stock Alert", "Canon CLI-526 Ink Cartridge is running low (3 remaining)"),
            ("maintenance_due", "Maintenance Due", "Canon EOS R5 is due for sensor cleaning"),
            ("general", "Welcome to StudioFlow", "Your studio management system is ready to use"),
        ]
        count = 0
        for ntype, title, message in notif_data:
            Notification.objects.get_or_create(
                user=random.choice(users),
                title=title,
                defaults={
                    "notification_type": ntype,
                    "message": message,
                    "is_read": random.choice([True, False]),
                },
            )
            count += 1
        self.stdout.write(f"  Notifications: {count}")
