// E2E test: marketing and public pages accessibility and render.
//
// User journey tested:
//   An unauthenticated visitor browses the marketing site, navigates
//   to Pricing, Contact, and Blog, and submits the demo request form.
//
// Test cases:
//   test_home_page_loads_hero_section_without_errors
//     — navigates to /, asserts HeroSection heading is visible
//   test_pricing_page_renders_pricing_table
//     — navigates to /pricing, asserts PricingTable cards are visible
//   test_contact_page_renders_demo_request_form
//     — navigates to /contact, asserts DemoRequestForm inputs are present
//   test_demo_request_form_validation_shows_errors_on_empty_submit
//     — clicks Submit without filling fields, asserts validation messages
//   test_blog_list_page_renders_post_list
//     — navigates to /blog, asserts at least one post title is visible
//   test_navigation_to_product_page_succeeds
//     — clicks Product link in MarketingNav, asserts URL is /product
//   test_footer_contains_privacy_and_terms_links
//     — asserts href links to /legal/privacy and /legal/terms in footer
