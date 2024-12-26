import { ImageResponse } from 'next/og'

export const runtime = 'edge'

export async function GET() {
  return new ImageResponse(
    (
      <div
        style={{
          height: '100%',
          width: '100%',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: 'rgb(24 24 27)',
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        {/* Background gradient */}
        <div
          style={{
            position: 'absolute',
            inset: 0,
            background: 'linear-gradient(to bottom, rgba(59, 130, 246, 0.1), rgba(239, 68, 68, 0.1))',
            opacity: 0.6,
          }}
        />

        {/* Light beams */}
        <div
          style={{
            position: 'absolute',
            bottom: '-10%',
            left: '25%',
            width: '2px',
            height: '50%',
            background: 'rgba(59, 130, 246, 0.3)',
            transform: 'rotate(45deg)',
            filter: 'blur(20px)',
          }}
        />
        <div
          style={{
            position: 'absolute',
            bottom: '-10%',
            right: '25%',
            width: '2px',
            height: '50%',
            background: 'rgba(239, 68, 68, 0.3)',
            transform: 'rotate(-45deg)',
            filter: 'blur(20px)',
          }}
        />

        {/* Content */}
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            position: 'relative',
            padding: '60px',
          }}
        >
          <div 
            style={{ 
              position: 'relative',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
            }}
          >
            {/* Palm tree */}
            <div
              style={{
                position: 'absolute',
                right: '-56px',
                top: '-40px',
                fontSize: '72px',
                transform: 'rotate(12deg)',
                filter: 'drop-shadow(0 0 20px rgba(74, 222, 128, 0.3))',
              }}
            >
              🌴
            </div>

            <h1
              style={{
                fontSize: '120px',
                fontFamily: 'system-ui',
                fontWeight: 'bold',
                color: '#ef4444',
                textShadow: '0 0 40px rgba(239, 68, 68, 0.4)',
                margin: 0,
                lineHeight: 1.1,
                letterSpacing: '-0.02em',
              }}
            >
              Rick's Vision
            </h1>
            <p
              style={{
                fontSize: '48px',
                fontFamily: 'system-ui',
                color: '#60a5fa',
                textShadow: '0 0 25px rgba(96, 165, 250, 0.4)',
                margin: '24px 0 0 0',
                letterSpacing: '-0.01em',
              }}
            >
              Get texts on how the line is looking
            </p>
          </div>
        </div>
      </div>
    ),
    {
      width: 1200,
      height: 630,
    }
  )
} 