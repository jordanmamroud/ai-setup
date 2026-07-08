# Example Findings (calibration set)

Real findings from the June 10, 2026 baseline pass. Use these to calibrate severity and finding style: exact quote, location, why it matters to a user. When a new finding resembles one of these, match its severity.

## error — phone uniqueness violated (check 7)
> (888) 995-5317 displayed on jm-remodeling-special1, jm-bathroom-remodeling, AND jm-fbbath. (800) 510-4710 on jm-refacing-ppc and jm-remarketing-special. (833) 741-5008 on jm-remodeling-fbspecial and jm-refacing-fbspecial.

Only 3 numbers across 7 pages; calls from different campaigns are indistinguishable. One finding per shared number, listing all pages.

## error — empty tel link / sentence with a hole (checks 1 + 3)
> jm-fbbath, "Free Design" section: "Fill out the form or call [](tel:) to schedule your free design."

The phone value failed to render: empty display text AND empty tel: href. A user reads a broken sentence and the link dials nothing.

## error — same-page offer contradiction (check 5)
> jm-remodeling-special1: hero headline "Get Your Dream Kitchen For Less With 40% Off Installation", but FAQ #6 says "our current 30% off installation offer", footer banner says "30% Off Installation Ends" / "lock in 30% off installation", and the popup modal says "Lock In 30% Off Installation".

Four offer statements, two values. Report as ONE finding listing every location and both values.

## error — expired hard date in legal copy (check 5)
> jm-remarketing-special, Offer Details: "Homeowner must complete their free design consultation by 07/08/2024 to qualify for this promotion."

Two years past. Users are being shown a dead offer condition.

## informational — JS-rendered deadline handled correctly (check 5)
> jm-bathroom-remodeling hero: "50% Off Installation Until" with no visible date.

Correct handling: grep source for the countdown script's date before flagging. Only an error if no date exists anywhere in the source (then also a crawlability warning) or if the embedded date is past.

## warning — hero offer broader than disclaimer scope (check 5)
> jm-bathroom-remodeling: hero promises "50% Off Installation" generally; Offer Details says "Discount applies to the installation of new tub to shower conversion only."

Possibly intentional legal scoping → warning, not error. pages.md marks this one as known.

## warning — meta phone appears nowhere on page (check 4)
> jm-refacing-ppc, jm-remarketing-special, jm-refacing-fbspecial meta descriptions: "Call 866-776-4119." That number is absent from all seven pages.

Searchers see meta descriptions and may dial a stale tracking number.

## nit — typos (check 1)
> jm-refacing-ppc hero bullet: "Hundreds of styles too choose from" (too → to)
> jm-refacing-ppc, step 3: "backed by our industry leading 11 warranty" (missing "year")
> jm-fbbath section heading: "Why Our Clients Choosing Us?" (missing "Are")
> jm-bathroom-remodeling testimonial template text: "There were no hassles and the we love our new bathroom!" (injected "the" — template find/replace artifact, flagged even inside a testimonial)

## nit — stale brand fact (check 8)
> Legacy pages (jm-remarketing-special, jm-refacing-fbspecial, jm-fbbath) say "45+ years"; new-template pages say "47+ years."

True-but-stale copy drift across templates.

## nit — tel href formatting inconsistency (check 4)
> jm-bathroom-remodeling footer: `tel:(888)%20995-5317` while every other instance uses `tel:8889955317`.

Same digits, dials fine — formatting nit only.
