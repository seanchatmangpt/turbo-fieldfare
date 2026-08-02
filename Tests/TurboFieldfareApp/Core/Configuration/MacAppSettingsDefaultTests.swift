import Testing
@testable import TurboFieldfareAppCore

@Suite struct MacAppSettingsDefaultTests {
    @Test func noArgumentInitializerPreservesForkDefault() {
        #expect(MacAppSettings().contextTokens
            == AppContextLengthOption.sixtyFourK.tokens)
    }
}
