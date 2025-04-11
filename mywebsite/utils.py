import csv
import logging
from io import TextIOWrapper
from datetime import datetime
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Product, ProductCategory, ProductVariant

logger = logging.getLogger(__name__)

def import_csv(file, update_existing=False):
    """
    Processes CSV file for bulk product import
    Args:
        file: Uploaded CSV file object
        update_existing: Boolean to update existing products
    Returns:
        Tuple: (success_count, error_count, errors)
    """
    success_count = 0
    error_count = 0
    errors = []
    
    try:
        decoded_file = TextIOWrapper(file, encoding='utf-8-sig')
        reader = csv.DictReader(decoded_file)
        
        with transaction.atomic():
            for row_num, row in enumerate(reader, 1):
                try:
                    # ===== VALIDATE REQUIRED FIELDS =====
                    required_fields = ['product_code', 'name', 'category', 'status']
                    for field in required_fields:
                        if not row.get(field):
                            raise ValidationError(f"Missing required field: {field}")
                    
                    # ===== PRODUCT CREATION/UPDATION =====
                    product_code = row['product_code'].strip()
                    defaults = {
                        'name': row['name'].strip(),
                        'description': row.get('description', '').strip(),
                        'status': row['status'].lower(),
                        'launch_date': parse_date(row.get('launch_date')),
                    }
                    
                    # Get or create category
                    category, _ = ProductCategory.objects.get_or_create(
                        name=row['category'].strip(),
                        defaults={'description': row.get('category_description', '')}
                    )
                    defaults['category'] = category
                    
                    if update_existing:
                        product, created = Product.objects.update_or_create(
                            product_code=product_code,
                            defaults=defaults
                        )
                    else:
                        product, created = Product.objects.get_or_create(
                            product_code=product_code,
                            defaults=defaults
                        )
                        if not created:
                            raise ValidationError("Product already exists (disable 'update existing' to skip)")
                    
                    # ===== VARIANT PROCESSING =====
                    if row.get('variant_name'):
                        variant_data = {
                            'name': row['variant_name'].strip(),
                            'size': row.get('variant_size', ''),
                            'packaging_type': row.get('variant_packaging', 'bottle').lower(),
                            'barcode': row.get('barcode', '').strip(),
                            'status': row.get('variant_status', row['status']).lower()
                        }
                        
                        ProductVariant.objects.update_or_create(
                            product=product,
                            barcode=variant_data['barcode'],
                            defaults=variant_data
                        )
                    
                    success_count += 1
                
                except Exception as e:
                    error_count += 1
                    errors.append({
                        'row': row_num,
                        'product_code': row.get('product_code', 'N/A'),
                        'error': str(e)
                    })
                    logger.error(f"Row {row_num} error: {str(e)}")
                    
    except Exception as e:
        logger.critical(f"CSV import failed: {str(e)}")
        raise
    
    return success_count, error_count, errors

def parse_date(date_str):
    """Parse multiple date formats from CSV"""
    if not date_str:
        return None
    
    formats = [
        '%Y-%m-%d',  # 2023-12-31
        '%m/%d/%Y',  # 12/31/2023
        '%d-%b-%y',  # 31-Dec-23
        '%Y%m%d'     # 20231231
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue
    
    raise ValidationError(f"Invalid date format: {date_str}")