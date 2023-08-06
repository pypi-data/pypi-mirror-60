from setuptools import setup  # type: ignore
setup(
    author_email="mateus.amin@cleardata.com, bentron.drew@cleardata.com",
    author="Mateus Amin, Bentron Drew",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description=
    "An AWS IAM authentication package for Requests. Supported services: API Gateway v1",
    install_requires=["botocore>=1.14.0", "requests>=2.21.0"],
    keywords=
    "AWS IAM authentication auth AWS amazon API Gateway v1 Requests Signature v4",
    long_description_content_type="text/markdown",
    long_description=open('README.md').read(),
    name="requests_aws_iam_auth",
    packages=['requests_aws_iam_auth'],
    project_urls={
        "Bug Tracker":
        "https://github.com/mateusamin/requests-aws-iam-auth/issues",
        "Documentation":
        "https://github.com/MateusAmin/requests-aws-iam-auth/blob/master/README.md",
        "Source Code": "https://github.com/mateusamin/requests-aws-iam-auth/",
    },
    python_requires='>=3.7.0',
    url="https://github.com/mateusamin/requests-aws-iam-auth/",
    version="0.2.0",
)
