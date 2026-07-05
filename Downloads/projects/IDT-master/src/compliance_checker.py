from typing import List, Dict, Any
import logging
from pathlib import Path
import yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComplianceChecker:
    def __init__(self):
        """Initialize the compliance checker."""
        self.compliance_rules = self._load_compliance_rules()
    
    def _load_compliance_rules(self) -> Dict[str, Any]:
        """Load compliance rules from YAML configuration file."""
        try:
            config_path = Path(__file__).parent.parent / "config" / "compliance_rules.yaml"
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)['compliance_rules']
        except Exception as e:
            logger.error(f"Error loading compliance rules: {str(e)}")
            # Return default rules if config file not found
            return self._get_default_rules()
    
    def _get_default_rules(self) -> Dict[str, Any]:
        """Get default compliance rules if config file is not available."""
        return {
            'foreign_currency': {
                'name': 'Foreign Currency Transactions',
                'part': 'Notes to Accounts/Schedules',
                'sub_part': 'Foreign currency transactions',
                'description': 'Check for foreign currency transaction disclosures and compliance with GST rules',
                'keywords': ['foreign currency', 'exchange rate', 'currency risk', 'forex', 'USD', 'EUR'],
                'verification_prompt': 'Verify if foreign currency transactions are properly disclosed and comply with GST regulations. Check for proper documentation and tax implications.'
            },
            'related_party': {
                'name': 'Related Party Transactions',
                'description': 'Check for related party transaction disclosures as per Rule 28 of CGST Rules',
                'keywords': ['related party', 'related parties', 'associate', 'subsidiary', 'joint venture', 'affiliate'],
                'verification_prompt': 'Verify if related party transactions are properly disclosed and comply with Rule 28 of CGST Rules. Check for proper documentation and arm\'s length pricing.'
            },
            'revenue_recognition': {
                'name': 'Revenue Recognition',
                'description': 'Check for proper revenue recognition policies and GST compliance',
                'keywords': ['revenue', 'income', 'sales', 'turnover', 'revenue recognition', 'accrual'],
                'verification_prompt': 'Verify if revenue recognition policies are properly disclosed and comply with accounting standards and GST regulations.'
            },
            'income_tax': {
                'name': 'Income Tax Disclosures',
                'description': 'Check for income tax disclosures and compliance',
                'keywords': ['income tax', 'tax expense', 'deferred tax', 'tax provision', 'taxation'],
                'verification_prompt': 'Verify if income tax disclosures are complete and comply with applicable tax regulations.'
            },
            'capital_work': {
                'name': 'Capital Work in Progress (CWIP)',
                'description': 'Check for CWIP disclosures and ITC eligibility',
                'keywords': ['capital work in progress', 'CWIP', 'work in progress', 'construction', 'development'],
                'verification_prompt': 'Verify if CWIP is properly disclosed and check for ITC eligibility and compliance with GST rules.'
            },
            'fixed_assets': {
                'name': 'Fixed Assets and ITC',
                'description': 'Check for fixed asset disclosures and ITC reversals',
                'keywords': ['fixed assets', 'property plant equipment', 'PPE', 'depreciation', 'ITC reversal'],
                'verification_prompt': 'Verify if fixed assets are properly disclosed and check for ITC reversals and compliance with GST rules.'
            }
        }
    
    def get_compliance_rules(self) -> Dict[str, Any]:
        """Get the loaded compliance rules."""
        return self.compliance_rules
    
    def get_rules_by_part(self) -> Dict[str, List[Dict[str, Any]]]:
        """Group compliance rules by part for better organization."""
        rules_by_part = {}
        for rule_key, rule in self.compliance_rules.items():
            part = rule.get('part', 'Unknown')
            if part not in rules_by_part:
                rules_by_part[part] = []
            rules_by_part[part].append({
                'key': rule_key,
                'name': rule.get('name', ''),
                'sub_part': rule.get('sub_part', ''),
                'description': rule.get('description', ''),
                'verification_points': rule.get('verification_points', [])
            })
        return rules_by_part
    
    def get_impact_rules(self) -> Dict[str, Any]:
        """Get only rules that have GST impact (exclude 'No Impact' items)."""
        impact_rules = {}
        for rule_key, rule in self.compliance_rules.items():
            if 'No Impact' not in rule.get('part', ''):
                impact_rules[rule_key] = rule
        return impact_rules
    
    def get_no_impact_rules(self) -> Dict[str, Any]:
        """Get only rules that have no GST impact."""
        no_impact_rules = {}
        for rule_key, rule in self.compliance_rules.items():
            if 'No Impact' in rule.get('part', ''):
                no_impact_rules[rule_key] = rule
        return no_impact_rules
    
    def add_custom_rule(self, rule_key: str, rule: Dict[str, Any]):
        """Add a custom compliance rule."""
        self.compliance_rules[rule_key] = rule
        logger.info(f"Added custom compliance rule: {rule_key}")
        
    def remove_rule(self, rule_key: str):
        """Remove a compliance rule."""
        if rule_key in self.compliance_rules:
            del self.compliance_rules[rule_key]
            logger.info(f"Removed compliance rule: {rule_key}")
        else:
            logger.warning(f"Compliance rule not found: {rule_key}")
    
    def list_rules(self) -> List[str]:
        """List all available compliance rules."""
        return list(self.compliance_rules.keys())
    
    def get_rule_details(self, rule_key: str) -> Dict[str, Any]:
        """Get details of a specific compliance rule."""
        return self.compliance_rules.get(rule_key, {})
    
    def validate_rule(self, rule: Dict[str, Any]) -> bool:
        """Validate if a compliance rule has all required fields."""
        required_fields = ['name', 'part', 'sub_part', 'description', 'keywords', 'verification_prompt']
        return all(field in rule for field in required_fields)
    
    def export_rules(self, output_path: str):
        """Export compliance rules to a YAML file."""
        try:
            config_data = {'compliance_rules': self.compliance_rules}
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_data, f, default_flow_style=False, indent=2, allow_unicode=True)
            logger.info(f"Compliance rules exported to: {output_path}")
        except Exception as e:
            logger.error(f"Error exporting compliance rules: {str(e)}")
            raise
    
    def import_rules(self, input_path: str):
        """Import compliance rules from a YAML file."""
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            if 'compliance_rules' in config_data:
                self.compliance_rules = config_data['compliance_rules']
                logger.info(f"Compliance rules imported from: {input_path}")
            else:
                raise ValueError("Invalid compliance rules file format")
        except Exception as e:
            logger.error(f"Error importing compliance rules: {str(e)}")
            raise
    
    def get_compliance_summary(self) -> Dict[str, Any]:
        """Get a summary of compliance rules by category."""
        impact_rules = self.get_impact_rules()
        no_impact_rules = self.get_no_impact_rules()
        rules_by_part = self.get_rules_by_part()
        
        return {
            'total_rules': len(self.compliance_rules),
            'impact_rules': len(impact_rules),
            'no_impact_rules': len(no_impact_rules),
            'parts': list(rules_by_part.keys()),
            'rules_by_part': rules_by_part
        }