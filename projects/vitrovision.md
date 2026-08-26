# VitroVision

**Status:** in-progress (research)
**Repo:** `github.com/peeradon4778/VitroVision`
**Ownership:** mine

Zero-shot computer-vision model using **SAM3** to analyze in-vitro tissue-culture plantlets and predict their **readiness for nursery transfer** (*pre-acclimatization* stage). YSC 2027 school research project.

## Problem
Plantlets in tissue culture need to be judged ready for transfer out of the lab. Human judgment is subjective and slow.

## Approach / What it does
Zero-shot segmentation / classification on plantlet images to detect readiness. Tested on a batch of bird's-eye-chili bottles → readiness + "not ready" + "ROI unclear" buckets.

## Tech
SAM3 · Python · computer vision

## Key results & links
- [ ] Update with benchmark numbers + demo
- Repo: `github.com/peeradon4778/VitroVision`

## Next
- [ ] Publish to Hugging Face (model + Space demo)
- [ ] Add quantitative metrics
