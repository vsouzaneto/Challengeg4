import { expect, test } from "@playwright/test";
import { isEmbeddedInHost } from "../../client/src/lib/embed";

test.describe("isEmbeddedInHost", () => {
  test("should hide chrome when the app is framed by the host", () => {
    expect(isEmbeddedInHost("", true)).toBe(true);
  });

  test("should hide chrome when embed=1 is present", () => {
    expect(isEmbeddedInHost("?embed=1", false)).toBe(true);
  });

  test("should keep chrome when the app is standalone", () => {
    expect(isEmbeddedInHost("", false)).toBe(false);
    expect(isEmbeddedInHost("?room=churn", false)).toBe(false);
  });
});
