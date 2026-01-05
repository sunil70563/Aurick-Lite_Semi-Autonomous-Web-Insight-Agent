# Demo Target Website

This demo uses **Sauce Demo** (Swag Labs), a public e-commerce website standard for QA testing.

**URL**: `https://www.saucedemo.com/`

### Why e-commerce?
- **Clear user intent**: Browse → View → Add to Cart.
- **Rich UI interactions**: Logins, filters, product grids.
- **Common UX pitfalls**: Valid state for detecting issues.
- **Strong alignment** with Aurick’s real-world QA goals.

### What the agent does
1. **Identifies the page type** ("This is a login page").
2. **Chooses a realistic user action** (e.g., "Login with standard_user").
3. **Interacts autonomously** (Clicks Login).
4. **Observes results** (Product grid loads).
5. **Flags confusing or broken behavior** (if any).

This mirrors how a human QA engineer would explore a product.
