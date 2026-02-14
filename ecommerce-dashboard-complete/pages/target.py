"""
TARGETED FIX FOR REMAINING DASHBOARD ERRORS

This script fixes the 2 remaining errors:
1. Line 545: st.metric error in Conversion Funnel
2. Line 1024: Date comparison error in Customer Segmentation

USAGE:
python targeted_fix.py

This will patch your dashboard.py file directly.
Make a backup first if needed!
"""

import shutil
import os

def create_backup():
    """Create backup of dashboard.py"""
    if os.path.exists('dashboard.py'):
        shutil.copy('dashboard.py', 'dashboard_backup.py')
        print("✅ Backup created: dashboard_backup.py")
        return True
    else:
        print("❌ dashboard.py not found!")
        return False

def apply_targeted_fixes():
    """Apply surgical fixes to specific problematic lines"""
    
    if not os.path.exists('dashboard.py'):
        print("❌ Error: dashboard.py not found")
        return False
    
    print("\n📖 Reading dashboard.py...")
    with open('dashboard.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fixed_lines = []
    fixes_applied = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # ================================================================
        # FIX 1: Line ~545 - st.metric with problematic delta
        # ================================================================
        if i > 520 and i < 600 and 'st.metric(' in line and '"Product Views"' in line:
            print(f"\n🔧 Found st.metric at line {i+1}")
            
            # Collect the entire st.metric call (may span multiple lines)
            metric_block = [line]
            j = i + 1
            paren_count = line.count('(') - line.count(')')
            
            while paren_count > 0 and j < len(lines):
                metric_block.append(lines[j])
                paren_count += lines[j].count('(') - lines[j].count(')')
                j += 1
            
            # Check if this is a problematic metric
            metric_text = ''.join(metric_block)
            
            if 'delta=' in metric_text and 'drop-off' in metric_text:
                # Replace with fixed version
                indent = ' ' * (len(line) - len(line.lstrip()))
                
                fixed_lines.append(f'{indent}st.metric(\n')
                fixed_lines.append(f'{indent}    "Product Views",\n')
                fixed_lines.append(f'{indent}    f"{{product_views:,}}",\n')
                fixed_lines.append(f'{indent}    f"{{product_view_rate:.1f}}%"\n')
                fixed_lines.append(f'{indent})\n')
                fixed_lines.append(f'{indent}if drop_off_1 > 0:\n')
                fixed_lines.append(f'{indent}    st.caption(f"⬇️ {{drop_off_1:.1f}}% drop-off")\n')
                
                fixes_applied.append(f"Fixed Product Views st.metric at line {i+1}")
                i = j  # Skip the lines we just replaced
                continue
        
        # Similar fix for "Add to Cart"
        if i > 520 and i < 600 and 'st.metric(' in line and '"Add to Cart"' in line:
            metric_block = [line]
            j = i + 1
            paren_count = line.count('(') - line.count(')')
            
            while paren_count > 0 and j < len(lines):
                metric_block.append(lines[j])
                paren_count += lines[j].count('(') - lines[j].count(')')
                j += 1
            
            metric_text = ''.join(metric_block)
            
            if 'delta=' in metric_text and 'drop-off' in metric_text:
                indent = ' ' * (len(line) - len(line.lstrip()))
                
                fixed_lines.append(f'{indent}st.metric(\n')
                fixed_lines.append(f'{indent}    "Add to Cart",\n')
                fixed_lines.append(f'{indent}    f"{{cart_adds:,}}",\n')
                fixed_lines.append(f'{indent}    f"{{cart_rate:.1f}}%"\n')
                fixed_lines.append(f'{indent})\n')
                fixed_lines.append(f'{indent}if drop_off_2 > 0:\n')
                fixed_lines.append(f'{indent}    st.caption(f"⬇️ {{drop_off_2:.1f}}% drop-off")\n')
                
                fixes_applied.append(f"Fixed Add to Cart st.metric at line {i+1}")
                i = j
                continue
        
        # Similar fix for "Purchase"
        if i > 520 and i < 600 and 'st.metric(' in line and '"Purchase"' in line:
            metric_block = [line]
            j = i + 1
            paren_count = line.count('(') - line.count(')')
            
            while paren_count > 0 and j < len(lines):
                metric_block.append(lines[j])
                paren_count += lines[j].count('(') - lines[j].count(')')
                j += 1
            
            metric_text = ''.join(metric_block)
            
            if 'delta=' in metric_text and 'drop-off' in metric_text:
                indent = ' ' * (len(line) - len(line.lstrip()))
                
                fixed_lines.append(f'{indent}st.metric(\n')
                fixed_lines.append(f'{indent}    "Purchase",\n')
                fixed_lines.append(f'{indent}    f"{{purchases:,}}",\n')
                fixed_lines.append(f'{indent}    f"{{purchase_rate:.1f}}%"\n')
                fixed_lines.append(f'{indent})\n')
                fixed_lines.append(f'{indent}if drop_off_3 > 0:\n')
                fixed_lines.append(f'{indent}    st.caption(f"⬇️ {{drop_off_3:.1f}}% drop-off")\n')
                
                fixes_applied.append(f"Fixed Purchase st.metric at line {i+1}")
                i = j
                continue
        
        # ================================================================
        # FIX 2: Line ~1024 - Date comparison
        # ================================================================
        if i > 1000 and i < 1050:
            # Look for the date comparison pattern
            if "df['last_order_date'] >= filters['start_date'].date()" in line:
                print(f"\n🔧 Found date comparison at line {i+1}")
                
                # Check if it's part of the filtering block
                if i > 0 and 'df_filtered' in lines[i-1]:
                    # Add datetime conversion before the filter
                    indent = ' ' * (len(line) - len(line.lstrip()))
                    
                    # Insert conversion line
                    fixed_lines.append(f'{indent}# Convert to datetime for comparison\n')
                    fixed_lines.append(f"{indent}df['last_order_date'] = pd.to_datetime(df['last_order_date'])\n")
                    fixed_lines.append(f'{indent}\n')
                    
                    fixes_applied.append(f"Added datetime conversion at line {i+1}")
                
                # Fix the comparison by removing .date()
                fixed_line = line.replace(".date()", "")
                fixed_lines.append(fixed_line)
                
                fixes_applied.append(f"Fixed date comparison at line {i+1}")
                i += 1
                continue
            
            # Also catch the second part of the comparison
            if "df['last_order_date'] <= filters['end_date'].date()" in line:
                fixed_line = line.replace(".date()", "")
                fixed_lines.append(fixed_line)
                i += 1
                continue
        
        # Default: keep line as-is
        fixed_lines.append(line)
        i += 1
    
    # ================================================================
    # Write fixed file
    # ================================================================
    if not fixes_applied:
        print("\n⚠️  No fixes were applied. Your code may have different formatting.")
        print("   Try the manual fixes in DASHBOARD_FIXES.md")
        return False
    
    print("\n💾 Writing fixes...")
    with open('dashboard.py', 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print("\n" + "="*60)
    print("✅ FIXES APPLIED SUCCESSFULLY!")
    print("="*60)
    print("\nChanges made:")
    for i, fix in enumerate(fixes_applied, 1):
        print(f"  {i}. {fix}")
    
    print("\n🚀 Your dashboard.py has been fixed!")
    print("\nNext steps:")
    print("  1. Restart your Streamlit server")
    print("  2. Refresh the browser")
    print("  3. Test the Conversion Funnel and Customer Segmentation pages")
    print("\nIf you need to restore: dashboard_backup.py")
    print("="*60)
    
    return True

if __name__ == "__main__":
    print("="*60)
    print("TARGETED DASHBOARD FIX")
    print("="*60)
    print("\nThis will fix:")
    print("  • Line 545: st.metric error (Conversion Funnel)")
    print("  • Line 1024: Date comparison error (Customer Segmentation)")
    
    # Create backup
    if not create_backup():
        print("\n❌ Cannot proceed without dashboard.py")
        exit(1)
    
    # Apply fixes
    success = apply_targeted_fixes()
    
    if success:
        print("\n✅ Done! Restart Streamlit to see the changes.")
        exit(0)
    else:
        print("\n⚠️  Auto-fix couldn't be applied.")
        print("Use the manual fix guide in DASHBOARD_FIXES.md")
        exit(1)